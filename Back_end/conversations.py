#对话管理
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import User, Conversation, Message
from auth import get_current_user
from datetime import datetime
import logging
import os
import json
import dashscope
from experiment_matcher import DatabaseExperimentMatcher

# 配置logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# AI API配置
AI_API_KEY = "sk-a0479628f48b408782fe9cc4e3e838a7"
# 配置dashscope API密钥
dashscope.api_key = AI_API_KEY
APP_ID = "1bf02b5a8b1e4edea526f38365bdaac8"

# 初始化实验匹配器
experiment_matcher = DatabaseExperimentMatcher()

# 消息模型
class MessageModel(BaseModel):
    role: str  # 'user' 或 'assistant'
    content: str

# 聊天请求模型
class ChatRequest(BaseModel):
    messages: list[MessageModel]  # 完整的对话历史

# 创建对话请求模型
class CreateConversationRequest(BaseModel):
    title: str = "新对话"

# 发送消息请求模型
class SendMessageRequest(BaseModel):
    content: str

# 对话管理接口
def register_router(app: FastAPI):
    # 获取用户的对话列表
    @app.get("/api/ceea/conversations")
    def get_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 获取当前用户的所有同时包含用户消息和AI回复的对话
        user_conversations = []
        conversations = db.query(Conversation).filter(Conversation.user_id == current_user.phone).all()
        
        for conversation in conversations:
            # 检查是否同时包含用户消息和AI回复
            has_user_msg = any(msg.sender_type == "user" for msg in conversation.messages)
            has_ai_msg = any(msg.sender_type == "assistant" for msg in conversation.messages)
            
            if has_user_msg and has_ai_msg:
                user_conversations.append({
                    "id": conversation.id,
                    "title": conversation.title,
                    "created_at": conversation.created_at,
                    "updated_at": conversation.updated_at
                })
        
        # 按更新时间倒序排列
        user_conversations.sort(key=lambda x: x["updated_at"], reverse=True)
        return user_conversations

    # 获取对话详情
    @app.get("/api/ceea/conversations/{id}")
    def get_conversation(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 获取指定对话的详情
        conversation = db.query(Conversation).filter(Conversation.id == id).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在")
        
        # 检查对话是否属于当前用户
        if conversation.user_id != current_user.phone:
            raise HTTPException(status_code=403, detail="无权访问该对话")
        
        # 转换消息为API响应格式
        messages = []
        for msg in conversation.messages:
            # 检查是否为视频消息
            is_video = False
            video_name = None
            if "上传的视频:" in msg.content:
                is_video = True
                # 提取视频文件名
                video_name_part = msg.content.split("上传的视频:")[-1].strip()
                # 如果还有其他内容，只取文件名部分
                if "\n" in video_name_part:
                    video_name = video_name_part.split("\n")[0].strip()
                else:
                    video_name = video_name_part
            
            messages.append({
                "id": msg.id,
                "conversation": msg.conversation_id,
                "sender_type": msg.sender_type,
                "content": msg.content,
                "created_at": msg.created_at,
                "is_video": is_video,
                "video_name": video_name
            })
        
        return {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "messages": messages
        }

    # 创建新对话
    @app.post("/api/ceea/conversations")
    def create_conversation(request: CreateConversationRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 创建新对话
        from datetime import datetime
        
        new_conversation = Conversation(
            user_id=current_user.phone,
            title=request.title,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            summary_generated=False
        )
        
        # 将新对话添加到数据库
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
        
        # 添加日志
        logging.info(f"创建新对话: {new_conversation}")
        
        return {
            "id": new_conversation.id,
            "user": new_conversation.user_id,
            "title": new_conversation.title,
            "created_at": new_conversation.created_at,
            "updated_at": new_conversation.updated_at,
            "messages": [],
            "summary_generated": new_conversation.summary_generated
        }

    #处理视频类请求
    @app.post("/api/ceea/conversations/{id}/video")
    async def upload_video(
            id: int,
            video: UploadFile = File(...),
            content: str = Form(None),  
            experiment_name: str = Form(None),  
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
    ):
        """上传视频并调用大模型分析，支持用户指定实验名称"""
        try:
            logging.info(f"收到视频上传请求，对话ID: {id}, 实验名称: {experiment_name}")

            # 1. 基础检查
            conversation = db.query(Conversation).filter(Conversation.id == id).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="对话不存在")
            if conversation.user_id != current_user.phone:
                raise HTTPException(status_code=403, detail="无权访问该对话")

            # 2. 如果用户提供了实验名称，直接更新对话标题
            final_exp_name = "通用化学实验"  # 默认值

            if experiment_name and experiment_name.strip():
                conversation.title = experiment_name.strip()
                final_exp_name = experiment_name.strip()
                db.commit()  # 立即保存标题修改

            # 3. 保存视频
            videos_dir = os.path.join(os.path.dirname(__file__), "videos")
            os.makedirs(videos_dir, exist_ok=True)
            video_path = os.path.join(videos_dir, video.filename)
            with open(video_path, "wb") as f:
                f.write(await video.read())

            # 4. 存入用户消息
            display_content = content if content else f"上传视频: {video.filename}"
            if experiment_name:
                display_content += f"\n(指定实验: {experiment_name})"

            user_message_db = Message(
                conversation_id=id, sender_type="user", content=display_content, created_at=datetime.now()
            )
            db.add(user_message_db)

            # 5. 构造 AI 提示词 (Prompt)
            # 关键修改：告诉 AI “用户已经说了这是什么实验，请基于此评估”
            json_structure = """
            {
                "experiment_name": "实验名称",
                "summary": "一句话评价",
                "steps": [
                    {"name": "步骤名称", "status": "success", "comment": "评价内容", "score": 20, "total_score": 20, "score_points": [{"point_name": "小点名称", "point": "得分点描述", "status": "pass", "score": 5}, {"point_name": "小点名称", "point": "失分点描述", "status": "fail", "score": 0, "deduction": 5}]
                ]
            }
            """
            context_hint = ""
            experiment_evaluation = ""
            
            context_hint = f"用户已明确该实验为：【{experiment_name}】。请直接基于该实验的标准操作流程进行评估，不需要再去猜测这是什么实验。"
            
            # 匹配评价模板
            matched_template = experiment_matcher.find_most_similar_experiment(experiment_name)
            if matched_template:
                experiment_evaluation = f"\n参考评价模板：\n{matched_template['experiment']['content']}"
                context_hint += f"\n已找到相关评价模板，相似度：{matched_template['similarity']:.2f}"

            prompt_text = f"""
            你是一名严厉的化学实验考核老师。请根据用户提供的实验名称和参考评价模板，分析视频。
            {context_hint}
            {experiment_evaluation}

            要求：
            1. 严格返回纯 JSON 格式。
            2. JSON中的 "experiment_name" 字段请直接填入用户提供的实验名称。
            3. 请基于参考评价模板中的每一个评分点进行详细评估，对了打勾（pass），错了打叉（fail）。
            4. 对于每个步骤，详细列出评价模板中的所有评分点，得分点标记为"pass"，失分点标记为"fail"，并在"deduction"字段中注明扣分数值。
            5. 确保每个评分点都有对应的评估结果、小点名称（point_name）、评分标准（point）、得分值（score）和扣分数值（如果是失分点）。
            6. 对于每个步骤，计算并返回该步骤的得分（score）和总分（total_score）。
            7. 数据结构模板：
            {json_structure}
            """

            # 6. 调用 AI
            ai_analysis_result = ""

            try:
                video_url = f"file://{video_path}"
                messages = [
                    {
                        'role': 'user',
                        'content': [
                            {'video': video_url, "fps": 1},
                            {'text': prompt_text}
                        ]
                    }
                ]

                response = dashscope.MultiModalConversation.call(
                    api_key=AI_API_KEY,
                    model='qwen3.6-plus',
                    messages=messages,
                )

                if hasattr(response, 'output') and response.output:
                    raw_content = response.output.choices[0].message.content[0]["text"]
                    ai_analysis_result = raw_content.replace("```json", "").replace("```", "").strip()
                    
                    try:
                        import json
                        result_json = json.loads(ai_analysis_result)
                        # 计算步骤得分总和
                        steps_total = sum(step.get('score', 0) for step in result_json.get('steps', []))
                        # 总是设置正确的总分
                        result_json['total_score'] = steps_total
                        ai_analysis_result = json.dumps(result_json, ensure_ascii=False)
                        logging.info(f"自动计算总分：{steps_total}")
                    except Exception as e:
                        logging.error(f"计算总分时出错: {str(e)}")

                else:
                    ai_analysis_result = '{"error": "API无响应"}'

            except Exception as e:
                logging.error(f"AI调用失败: {str(e)}")
                ai_analysis_result = '{"error": "AI服务不可用"}'

            # 7. 保存结果
            ai_message_db = Message(
                conversation_id=id, sender_type="assistant", content=ai_analysis_result, created_at=datetime.now()
            )
            db.add(ai_message_db)

            conversation.updated_at = datetime.now()
            db.commit()
            db.refresh(ai_message_db)

            return {
                "user_message": {
                    "id": user_message_db.id,
                    "content": user_message_db.content,
                    "is_video": True,
                    "sender_type": "user",
                    "created_at": user_message_db.created_at
                },
                "ai_message": {
                    "id": ai_message_db.id,
                    "content": ai_message_db.content,
                    "sender_type": "assistant",
                    "created_at": ai_message_db.created_at
                }
            }

        except Exception as e:
            logging.error(f"处理错误: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
