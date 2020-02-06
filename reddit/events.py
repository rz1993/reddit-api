"""
Event Processor class:
- Each module imports event_handler
- Each module registers its signals
- Each module registers is subscribers for its signals and other module's signals (no circular dependencies)
"""

class EventProcessor:
    _CREATE_EVENTS = {}
    _DELETE_EVENTS = {}
    _UPDATE_EVENTS = {}

    def __init__(self, app=None, db=None):
        if app and db:
            self.init_app(app, db)

    def init_app(self, app, db):
        if app.config.get('ENABLE_DB_EVENTS'):
            db.event.listen(
                db.session,
                'after_commit',
                self.after_commit
            )

    def after_commit(self, session):
        for obj in session._changes['add']:
            if obj.__class__ in self._CREATE_EVENTS:
                self._CREATE_EVENTS[obj.__class__].send(obj)

        for obj in session._changes['update']:
            if obj.__class__ in self._UPDATE_EVENTS:
                self._UPDATE_EVENTS[obj.__class__].send(obj)

        for obj in session._changes['delete']:
            if obj.__class__ in self._DELETE_EVENTS:
                self._DELETE_EVENTS[obj.__class__].send(obj)

    def register_crud_events(
        self,
        model_cls,
        create=None,
        update=None,
        delete=None
    ):
        if create:
            self._CREATE_EVENTS[model_cls] = create
        if update:
            self._UPDATE_EVENTS[model_cls] = update
        if delete:
            self._DELETE_EVENTS[model_cls] = delete
