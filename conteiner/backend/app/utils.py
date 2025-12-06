from fastapi import HTTPException, status

def raise_not_found(msg="Item not found"):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

def raise_unauthorized(msg="Unauthorized"):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)