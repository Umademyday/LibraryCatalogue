from contextlib import contextmanager


class UnitOfWork:
    def __init__(self, session_factory):
        self._session_factory = session_factory
        self.session = None

    @contextmanager
    def start(self):
        self.session = self._session_factory()
        try:
            yield self
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.close()
