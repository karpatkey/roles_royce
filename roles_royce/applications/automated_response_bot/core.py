from dataclasses import dataclass, field

from roles_royce.applications.automated_response_bot.utils import validate_webhook

from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Alert:
    id: str
    data: dict
    digitalSignature: str
    alert_id: str = field(init=False)
    chain: str = None
    name: str = None
    category: str = None
    status: str = None
    timestamp: str = None
    severity: str = None
    details: str = None
    involvedAssets: List[Dict[str, str]] = None
    riskTypeId: str = None
    riskTypeDescription: str = None
    context: Dict[str, str] = None
    txnHash: str = None

    def __post_init__(self):
        risk_insight = self.data.get('riskInsight', {})
        self.alert_id = risk_insight.get('id')
        self.chain = risk_insight.get('chain')
        self.name = risk_insight.get('name')
        self.category = risk_insight.get('category')
        self.status = risk_insight.get('status')
        self.timestamp = risk_insight.get('timestamp')
        self.severity = risk_insight.get('severity')
        self.details = risk_insight.get('details')
        self.involvedAssets = risk_insight.get('involvedAssets')
        self.riskTypeId = risk_insight.get('riskTypeId')
        self.riskTypeDescription = risk_insight.get('riskTypeDescription')
        self.context = risk_insight.get('context')
        self.txnHash = risk_insight.get('txnHash')

    @classmethod
    def from_webhook(cls, data: dict):
        return cls(
            id=data.get('id'),
            data=data,
            digitalSignature=data.get('digitalSignature')
        )
