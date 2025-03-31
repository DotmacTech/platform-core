from sqlalchemy.orm import Session
import logging

from app.db.session import engine, Base, SessionLocal
from app.core.settings import get_settings

# Import all models to ensure they are registered with SQLAlchemy
from app.modules.config.models import ConfigScope, ConfigItem, ConfigHistory
from app.modules.audit.models import AuditLog
from app.modules.feature_flags.models import FeatureFlag
from app.modules.logging.models import LogEntry
from app.modules.webhooks.models import WebhookEndpoint, WebhookSubscription, WebhookDelivery
from app.modules.notifications.models import Notification

settings = get_settings()
logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    """
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Initialize default data if needed
        db = SessionLocal()
        try:
            init_default_data(db)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def init_default_data(db: Session) -> None:
    """
    Initialize default data in the database.
    """
    # Create default config scopes if they don't exist
    default_scopes = ["system", "auth", "logging", "notifications"]
    for scope_name in default_scopes:
        scope = db.query(ConfigScope).filter(ConfigScope.name == scope_name).first()
        if not scope:
            scope = ConfigScope(
                name=scope_name,
                description=f"Default {scope_name} configuration scope"
            )
            db.add(scope)
    
    # Create default feature flags if they don't exist
    default_flags = [
        {
            "key": "enable_webhooks",
            "name": "Enable Webhooks",
            "description": "Enable webhook dispatching functionality",
            "enabled": True
        },
        {
            "key": "enable_notifications",
            "name": "Enable Notifications",
            "description": "Enable notification triggering functionality",
            "enabled": True
        },
        {
            "key": "enable_audit_logging",
            "name": "Enable Audit Logging",
            "description": "Enable audit logging for sensitive actions",
            "enabled": True
        }
    ]
    
    for flag_data in default_flags:
        flag = db.query(FeatureFlag).filter(FeatureFlag.key == flag_data["key"]).first()
        if not flag:
            flag = FeatureFlag(**flag_data)
            db.add(flag)
    
    # Commit all changes
    db.commit()
    logger.info("Default data initialized successfully")
