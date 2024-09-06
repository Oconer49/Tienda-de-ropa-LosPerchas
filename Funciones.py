def CreateID(collection):
    # Buscar el documento con el ID más alto
    ultimo_documento = collection.find_one(sort=[("_id", -1)])
    if ultimo_documento is None:
        return 1
    else:
        id = ultimo_documento["_id"] + 1
        return id