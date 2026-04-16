# 测试脚本：验证发送给AI的提示词
from experiment_matcher import DatabaseExperimentMatcher

# 初始化实验匹配器
matcher = DatabaseExperimentMatcher()

# 测试匹配乙酸乙酯的制备实验
test_input = "制备NaCl溶液"
matched_template = matcher.find_most_similar_experiment(test_input)

if matched_template:
    experiment_evaluation = f"\n参考评价模板：\n{matched_template['experiment']['content']}"
    context_hint = f"用户已明确该实验为：【{test_input}】。请直接基于该实验的标准操作流程进行评估，不需要再去猜测这是什么实验。"
    context_hint += f"\n已找到相关评价模板，相似度：{matched_template['similarity']:.2f}"
    
    json_structure = """
    {
        "experiment_name": "实验名称",
                "summary": "一句话评价",
                "steps": [
                    {"name": "步骤名称", "status": "success", "comment": "评价内容", "score": 20, "total_score": 20, "score_points": [{"point_name": "小点名称", "point": "得分点描述", "status": "pass", "score": 5}, {"point_name": "小点名称", "point": "失分点描述", "status": "fail", "score": 0, "deduction": 5}]
                ]
    }
    """
    
    prompt_text = f"""
    你是一名严厉的化学实验考核老师。请根据用户提供的实验名称和参考评价模板，分析视频。
    {context_hint}
    {experiment_evaluation}

    要求：
    1. 严格返回纯 JSON 格式。
    2. 如果用户提供了实验名称，JSON中的 "experiment_name" 字段请直接填入用户提供的名称。
    3. 请基于参考评价模板中的每一个评分点进行详细评估，对了打勾（pass），错了打叉（fail）。
    4. 对于每个步骤，详细列出评价模板中的所有评分点，得分点标记为"pass"，失分点标记为"fail"，并在"deduction"字段中注明扣分数值。
    5. 确保每个评分点都有对应的评估结果和扣分数值（如果是失分点）。
    6. 总分计算：根据评价模板中的总分标准，减去所有失分点的扣分数值，得到最终总分。确保总分与得分相加一致。
    7. 数据结构模板：
    {json_structure}
    """
    
    print("发送给AI的提示词:")
    print(prompt_text)
else:
    print("未找到匹配的实验模板")
