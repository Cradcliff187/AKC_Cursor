from datetime import datetime

class Bid:
    """Represents a bid or proposal in the system"""
    
    def __init__(self, id=None, name=None, client_id=None, project_id=None, 
                 created_by_id=None, status="Draft", version=1, bid_number=None,
                 proposal_date=None, valid_until=None, total_amount=0.0, 
                 labor_cost=0.0, material_cost=0.0, overhead_cost=0.0, profit_margin=0.0,
                 description=None, notes=None, terms_and_conditions=None,
                 client_message=None, client_response=None, client_response_date=None,
                 created_at=None, updated_at=None, file_path=None, original_filename=None):
        """Initialize a new Bid object"""
        self.id = id
        self.name = name
        self.client_id = client_id
        self.project_id = project_id
        self.created_by_id = created_by_id
        self.status = status if status else "Draft"
        self.version = version if version else 1
        self.bid_number = bid_number
        self.proposal_date = proposal_date if proposal_date else datetime.now().date()
        self.valid_until = valid_until
        self.total_amount = float(total_amount) if total_amount is not None else 0.0
        self.labor_cost = float(labor_cost) if labor_cost is not None else 0.0
        self.material_cost = float(material_cost) if material_cost is not None else 0.0
        self.overhead_cost = float(overhead_cost) if overhead_cost is not None else 0.0
        self.profit_margin = float(profit_margin) if profit_margin is not None else 0.0
        self.description = description
        self.notes = notes
        self.terms_and_conditions = terms_and_conditions
        self.client_message = client_message
        self.client_response = client_response
        self.client_response_date = client_response_date
        self.created_at = created_at if created_at else datetime.now()
        self.updated_at = updated_at if updated_at else datetime.now()
        self.file_path = file_path
        self.original_filename = original_filename
    
    @staticmethod
    def from_dict(data):
        """Create a Bid object from a dictionary"""
        return Bid(
            id=data.get('id'),
            name=data.get('name'),
            client_id=data.get('client_id'),
            project_id=data.get('project_id'),
            created_by_id=data.get('created_by_id'),
            status=data.get('status'),
            version=data.get('version'),
            bid_number=data.get('bid_number'),
            proposal_date=data.get('proposal_date'),
            valid_until=data.get('valid_until'),
            total_amount=data.get('total_amount'),
            labor_cost=data.get('labor_cost'),
            material_cost=data.get('material_cost'),
            overhead_cost=data.get('overhead_cost'),
            profit_margin=data.get('profit_margin'),
            description=data.get('description'),
            notes=data.get('notes'),
            terms_and_conditions=data.get('terms_and_conditions'),
            client_message=data.get('client_message'),
            client_response=data.get('client_response'),
            client_response_date=data.get('client_response_date'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            file_path=data.get('file_path'),
            original_filename=data.get('original_filename')
        )
    
    def to_dict(self):
        """Convert Bid object to a dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'client_id': self.client_id,
            'project_id': self.project_id,
            'created_by_id': self.created_by_id,
            'status': self.status,
            'version': self.version,
            'bid_number': self.bid_number,
            'proposal_date': self.proposal_date,
            'valid_until': self.valid_until,
            'total_amount': self.total_amount,
            'labor_cost': self.labor_cost,
            'material_cost': self.material_cost,
            'overhead_cost': self.overhead_cost,
            'profit_margin': self.profit_margin,
            'description': self.description,
            'notes': self.notes,
            'terms_and_conditions': self.terms_and_conditions,
            'client_message': self.client_message,
            'client_response': self.client_response,
            'client_response_date': self.client_response_date,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'file_path': self.file_path,
            'original_filename': self.original_filename
        } 