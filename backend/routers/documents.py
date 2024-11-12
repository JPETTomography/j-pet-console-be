import uproot
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
import database.models as models
from database.database import get_session_local  # Make sure your database session is imported

router = APIRouter()

@router.post("/create_sample")
def create_sample(db: Session = Depends(get_session_local)):
    file = uproot.open("./data/dabc_17334031817.tslot.calib.root")

    hist = file["TimeWindowCreator subtask 0 stats/LL_per_PM"]

    x = hist.axis().centers().tolist()
    y = hist.values().tolist()

    title = "Unstructured Data Example"
    data = {
        "x": x,
        "y": y,
    }
    example = models.Document(title=title, data=data)
    db.add(example)
    db.commit()
    
    return {"message": "Sample document created"}

@router.get("/get_sample")
def get_sample(db: Session = Depends(get_session_local)):
    return db.query(models.Document).one() or "No documents found."