from django.db.models import Model, QuerySet


def get_or_none(model: Model, *args, **kwargs) -> Model:
    """
    Gets single model entry or None for a given model
    based on selection args or kwargs
    Notes: Returns None on Model.DoesNotExist exception
    Params:
        model -> DB model to fetch
    Returns:
        Matched model object or None
    """
    try:
        if "prefetch_related" in kwargs:
            prefetch_data = kwargs.get("prefetch_related")
            del kwargs["prefetch_related"]
            if prefetch_data is not None:
                if isinstance(prefetch_data, str):
                    return model.objects.prefetch_related(prefetch_data).get(
                        *args, **kwargs
                    )
                else:
                    return model.objects.prefetch_related(*prefetch_data).get(
                        *args, **kwargs
                    )
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def filter_or_none(model: Model, *args, **kwargs) -> QuerySet:
    """
    Filters given model and QuerySet or None
    based on filter args or kwargs
    Notes: Returns None on Model.DoesNotExist exception
    Params:
        model -> DB model to fetch
    Returns:
        Matched model object or None
    """

    try:
        if "prefetch_related" in kwargs:
            prefetch_data = kwargs.get("prefetch_related")
            del kwargs["prefetch_related"]
            if prefetch_data is not None:
                if isinstance(prefetch_data, str):
                    return model.objects.filter(*args, **kwargs).prefetch_related(
                        prefetch_data
                    )
                return model.objects.filter(*args, **kwargs).prefetch_related(
                    *prefetch_data
                )
        return model.objects.filter(*args, **kwargs)
    except model.DoesNotExist:
        return None


def get_or_create(model: Model, *args, **kwargs) -> Model:
    """
    Fetches an existing model based on the selection args
    If a matching object cannot be found, creates a new object
    Notes: Does not save the new object model
    Params:
        models
    Returns:
        existing or new model instance
    """

    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return model(*args, **kwargs)
