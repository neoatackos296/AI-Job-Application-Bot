from datetime import datetime, timedelta
from models import Job, Application
from sqlalchemy import func
from typing import Dict

class JobAnalytics:
    def __init__(self, db_session):
        self.db = db_session
    
    def get_application_stats(self, days: int = 30) -> Dict:
        """Get application statistics for the past n days"""
        start_date = datetime.now() - timedelta(days=days)
        
        stats = {
            'total_applications': self.db.query(Application).count(),
            'successful_applications': self.db.query(Application)
                .filter(Application.status == 'success').count(),
            'response_rate': self._calculate_response_rate(),
            'top_companies': self._get_top_companies()
        }
        return stats

    def _calculate_response_rate(self):
        """Calculate the response rate of applications"""
        total_applications = self.db.query(Application).count()
        if total_applications == 0:
            return 0
        responded_applications = self.db.query(Application).filter(
            Application.status != 'pending').count()
        return (responded_applications / total_applications) * 100

    def _get_top_companies(self, limit: int = 5):
        """Get top companies by number of job postings"""
        return (
            self.db.query(Job.company_id, func.count(Job.id))
            .join(Application, Application.job_id == Job.id)
            .group_by(Job.company_id)
            .order_by(func.count(Job.id).desc())
            .limit(limit)
            .all()
        )