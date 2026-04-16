#通知管理
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import User, Notification
from auth import get_current_user

# 通知系统接口
def register_router(app: FastAPI):
    # 获取当前用户的通知列表（支持分页）
    @app.get("/api/ceea/notifications")
    def get_notifications(
        page: int = 1,
        page_size: int = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        try:
            # 查询当前用户的通知总数
            total_count = db.query(Notification).filter(
                Notification.receiver_id == current_user.phone
            ).count()

            # 计算总页数
            total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

            # 分页查询通知列表，按创建时间倒序
            notifications = db.query(Notification).filter(
                Notification.receiver_id == current_user.phone
            ).order_by(Notification.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

            # 构建响应数据
            notification_list = []
            for notif in notifications:
                # 获取发送者姓名
                sender = db.query(User).filter(User.phone == notif.sender_id).first()
                sender_name = sender.name if sender and sender.name else notif.sender_id

                notification_list.append({
                    "id": notif.id,
                    "title": notif.title,
                    "content": notif.content,
                    "notification_type": notif.notification_type,
                    "sender_id": notif.sender_id,
                    "sender_name": sender_name,
                    "related_id": notif.related_id,
                    "is_read": notif.is_read,
                    "created_at": notif.created_at.isoformat() if notif.created_at else None
                })

            return {
                "items": notification_list,
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        except Exception as e:
            print(f"获取通知列表失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取通知列表失败: {str(e)}")

    # 获取未读通知数量
    @app.get("/api/ceea/notifications/unread-count")
    def get_unread_count(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        try:
            # 统计当前用户的未读通知数
            unread_count = db.query(Notification).filter(
                Notification.receiver_id == current_user.phone,
                Notification.is_read == False
            ).count()

            return {
                "unread_count": unread_count
            }
        except Exception as e:
            print(f"获取未读数量失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取未读数量失败: {str(e)}")

    # 标记单条通知为已读
    @app.put("/api/ceea/notifications/{notification_id}/read")
    def mark_as_read(
        notification_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        try:
            # 查找通知
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()

            if not notification:
                raise HTTPException(status_code=404, detail="通知不存在")

            # 验证权限：只能标记自己的通知
            if notification.receiver_id != current_user.phone:
                raise HTTPException(status_code=403, detail="无权操作该通知")

            # 标记为已读
            notification.is_read = True
            db.commit()

            return {
                "message": "success",
                "notification_id": notification_id
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"标记已读失败: {e}")
            raise HTTPException(status_code=500, detail=f"标记已读失败: {str(e)}")

    # 全部标记为已读
    @app.put("/api/ceea/notifications/read-all")
    def mark_all_as_read(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        try:
            # 查询所有未读通知
            unread_notifications = db.query(Notification).filter(
                Notification.receiver_id == current_user.phone,
                Notification.is_read == False
            ).all()

            # 统计数量
            marked_count = len(unread_notifications)

            # 批量更新为已读
            for notification in unread_notifications:
                notification.is_read = True

            db.commit()

            return {
                "message": "success",
                "marked_count": marked_count
            }
        except Exception as e:
            print(f"全部标记已读失败: {e}")
            raise HTTPException(status_code=500, detail=f"全部标记已读失败: {str(e)}")
