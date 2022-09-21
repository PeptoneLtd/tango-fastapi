import logging

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from typing import List, Literal

import uvicorn
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import tango.predictor
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FastAPIInstrumentor.instrument_app(app)
logger = logging.getLogger("uvicorn.error")

valid_residues = re.compile('(?i)^[ARNDCHIQEGLKMFPSTWYV]+$')


class TangoRequest(BaseModel):
    name: str = "p0"
    ct: Literal['N', 'Y'] = 'N'
    nt: Literal['N', 'A', 'S'] = 'N'
    ph: float = Field(default=7.2, ge=0.0, le=14.0)
    te: float = Field(default=298.15, gt=0.0)
    io: float = Field(default=0.1, ge=0.0)
    seq: str

    @validator('seq')
    def must_only_contain_valid_residues(cls, v):
        if not valid_residues.search(v):
            raise ValueError(f"input sequence contains invalid amino acids")
        return v.upper()

@app.post("/v1/tango/aggregation", response_model=List[float])
async def v1_tango_aggregation(req: TangoRequest) -> List[float]:
    res = tango.predictor.run(name=req.name, ct=req.ct, nt=req.nt,
                              ph=req.ph, te=req.te, io=req.io, seq=req.seq)
    return [i['aggregation'] for i in res]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
