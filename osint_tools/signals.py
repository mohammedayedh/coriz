from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import OSINTSession, OSINTResult, OSINTActivityLog


@receiver(post_save, sender=OSINTSession)
def create_session_activity_log(sender, instance, created, **kwargs):
    """إنشاء سجل نشاط عند إنشاء جلسة جديدة"""
    if created:
        OSINTActivityLog.objects.create(
            user=instance.user,
            session=instance,
            action='session_started',
            description=f'تم بدء جلسة جديدة باستخدام أداة {instance.tool.name} للهدف: {instance.target}',
            ip_address=None,  # سيتم ملؤه في الـ view
            user_agent=''
        )


@receiver(pre_save, sender=OSINTSession)
def update_session_status(sender, instance, **kwargs):
    """تحديث حالة الجلسة وتتبع التوقيت"""
    if instance.pk:
        try:
            old_instance = OSINTSession.objects.get(pk=instance.pk)
            
            # إذا تغيرت الحالة من pending إلى running
            if old_instance.status == 'pending' and instance.status == 'running':
                instance.started_at = timezone.now()
                
            # إذا تغيرت الحالة إلى completed أو failed أو cancelled
            elif old_instance.status == 'running' and instance.status in ['completed', 'failed', 'cancelled']:
                if instance.started_at:
                    instance.completed_at = timezone.now()
                    instance.duration = instance.completed_at - instance.started_at
                    
                # إنشاء سجل نشاط للإكمال
                OSINTActivityLog.objects.create(
                    user=instance.user,
                    session=instance,
                    action='session_completed',
                    description=f'تم إكمال جلسة {instance.tool.name} بنتيجة: {instance.status}',
                    details={
                        'duration': str(instance.duration) if instance.duration else None,
                        'results_count': instance.results_count,
                        'error_message': instance.error_message if instance.status == 'failed' else None
                    }
                )
                
        except OSINTSession.DoesNotExist:
            pass


@receiver(post_save, sender=OSINTResult)
def update_session_results_count(sender, instance, created, **kwargs):
    """تحديث عدد النتائج في الجلسة"""
    if created:
        session = instance.session
        session.results_count = OSINTResult.objects.filter(session=session).count()
        session.save(update_fields=['results_count'])
        
        # إنشاء سجل نشاط للنتيجة الجديدة
        OSINTActivityLog.objects.create(
            user=session.user,
            session=session,
            action='result_exported',
            description=f'تم اكتشاف نتيجة جديدة من نوع: {instance.result_type}',
            details={
                'result_type': instance.result_type,
                'confidence': instance.confidence,
                'source': instance.source
            }
        )
