from flask import (
    Blueprint, flash, g, redirect, render_template, 
    request, session, url_for, jsonify
)
from app.routes.auth import login_required
from app.services.notifications import (
    get_user_notifications, get_notification_by_id, 
    mark_notification_as_read, mark_all_notifications_as_read,
    delete_notification, get_unread_notification_count
)

bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@bp.route('/')
@login_required
def list_notifications():
    """Show all notifications for the current user"""
    user_id = session.get('user_id')
    
    # Get filter parameters
    unread_only = request.args.get('unread_only') == 'true'
    notification_type = request.args.get('type')
    category = request.args.get('category')
    
    # Get notifications
    notifications = get_user_notifications(user_id, unread_only=unread_only)
    
    # Apply filters
    if notification_type:
        notifications = [n for n in notifications if n.notification_type == notification_type]
        
    if category:
        notifications = [n for n in notifications if n.category == category]
    
    # Get unread count for badge display
    unread_count = get_unread_notification_count(user_id)
    
    return render_template('notifications/index.html', 
                          notifications=notifications,
                          unread_count=unread_count)

@bp.route('/<notification_id>')
@login_required
def view_notification(notification_id):
    """View a single notification and mark it as read"""
    user_id = session.get('user_id')
    
    # Get the notification
    notification = get_notification_by_id(notification_id)
    
    if not notification:
        flash('Notification not found', 'error')
        return redirect(url_for('notifications.list_notifications'))
    
    # Check ownership
    if notification.user_id != user_id:
        flash('Access denied', 'error')
        return redirect(url_for('notifications.list_notifications'))
    
    # Mark as read
    if not notification.is_read:
        mark_notification_as_read(notification_id)
        notification.is_read = True
    
    # If there's an action URL, redirect to it
    if notification.action_url:
        return redirect(notification.action_url)
    
    # Otherwise show the notification detail
    return render_template('notifications/detail.html', notification=notification)

@bp.route('/<notification_id>/mark-read', methods=['POST'])
@login_required
def mark_read(notification_id):
    """Mark a notification as read (AJAX endpoint)"""
    user_id = session.get('user_id')
    
    # Get the notification
    notification = get_notification_by_id(notification_id)
    
    if not notification:
        return jsonify({'success': False, 'error': 'Notification not found'}), 404
    
    # Check ownership
    if notification.user_id != user_id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    # Mark as read
    result = mark_notification_as_read(notification_id)
    
    if result:
        return jsonify({
            'success': True, 
            'unread_count': get_unread_notification_count(user_id)
        })
    
    return jsonify({'success': False, 'error': 'Failed to mark notification as read'}), 500

@bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """Mark all notifications as read (AJAX endpoint)"""
    user_id = session.get('user_id')
    
    # Mark all as read
    result = mark_all_notifications_as_read(user_id)
    
    if result:
        return jsonify({'success': True, 'unread_count': 0})
    
    return jsonify({'success': False, 'error': 'Failed to mark all notifications as read'}), 500

@bp.route('/<notification_id>/delete', methods=['POST'])
@login_required
def delete(notification_id):
    """Delete a notification (AJAX endpoint)"""
    user_id = session.get('user_id')
    
    # Get the notification
    notification = get_notification_by_id(notification_id)
    
    if not notification:
        return jsonify({'success': False, 'error': 'Notification not found'}), 404
    
    # Check ownership
    if notification.user_id != user_id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    # Delete the notification
    result = delete_notification(notification_id)
    
    if result:
        return jsonify({
            'success': True, 
            'unread_count': get_unread_notification_count(user_id)
        })
    
    return jsonify({'success': False, 'error': 'Failed to delete notification'}), 500 