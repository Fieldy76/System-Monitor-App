import logging  # import logging
from logging.config import fileConfig  # from logging.config import fileConfig
  # blank line
from flask import current_app  # from flask import current_app
  # blank line
from alembic import context  # from alembic import context
  # blank line
# this is the Alembic Config object, which provides  # # this is the Alembic Config object, which provides
# access to the values within the .ini file in use.  # # access to the values within the .ini file in use.
config = context.config  # config = context.config
  # blank line
# Interpret the config file for Python logging.  # # Interpret the config file for Python logging.
# This line sets up loggers basically.  # # This line sets up loggers basically.
fileConfig(config.config_file_name)  # fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')  # logger = logging.getLogger('alembic.env')
  # blank line
  # blank line
def get_engine():  # def get_engine():
    try:  # try:
        # this works with Flask-SQLAlchemy<3 and Alchemical  # # this works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()  # return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):  # except (TypeError, AttributeError):
        # this works with Flask-SQLAlchemy>=3  # # this works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine  # return current_app.extensions['migrate'].db.engine
  # blank line
  # blank line
def get_engine_url():  # def get_engine_url():
    try:  # try:
        return get_engine().url.render_as_string(hide_password=False).replace(  # return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')  # '%', '%%')
    except AttributeError:  # except AttributeError:
        return str(get_engine().url).replace('%', '%%')  # return str(get_engine().url).replace('%', '%%')
  # blank line
  # blank line
# add your model's MetaData object here  # # add your model's MetaData object here
# for 'autogenerate' support  # # for 'autogenerate' support
# from myapp import mymodel  # # from myapp import mymodel
# target_metadata = mymodel.Base.metadata  # # target_metadata = mymodel.Base.metadata
config.set_main_option('sqlalchemy.url', get_engine_url())  # config.set_main_option('sqlalchemy.url', get_engine_url())
target_db = current_app.extensions['migrate'].db  # target_db = current_app.extensions['migrate'].db
  # blank line
# other values from the config, defined by the needs of env.py,  # # other values from the config, defined by the needs of env.py,
# can be acquired:  # # can be acquired:
# my_important_option = config.get_main_option("my_important_option")  # # my_important_option = config.get_main_option("my_important_option")
# ... etc.  # # ... etc.
  # blank line
  # blank line
def get_metadata():  # def get_metadata():
    if hasattr(target_db, 'metadatas'):  # if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]  # return target_db.metadatas[None]
    return target_db.metadata  # return target_db.metadata
  # blank line
  # blank line
def run_migrations_offline():  # def run_migrations_offline():
    """Run migrations in 'offline' mode.  # """Run migrations in 'offline' mode.
  # blank line
    This configures the context with just a URL  # This configures the context with just a URL
    and not an Engine, though an Engine is acceptable  # and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation  # here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.  # we don't even need a DBAPI to be available.
  # blank line
    Calls to context.execute() here emit the given string to the  # Calls to context.execute() here emit the given string to the
    script output.  # script output.
  # blank line
    """  # """
    url = config.get_main_option("sqlalchemy.url")  # url = config.get_main_option("sqlalchemy.url")
    context.configure(  # context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True  # url=url, target_metadata=get_metadata(), literal_binds=True
    )  # )
  # blank line
    with context.begin_transaction():  # with context.begin_transaction():
        context.run_migrations()  # context.run_migrations()
  # blank line
  # blank line
def run_migrations_online():  # def run_migrations_online():
    """Run migrations in 'online' mode.  # """Run migrations in 'online' mode.
  # blank line
    In this scenario we need to create an Engine  # In this scenario we need to create an Engine
    and associate a connection with the context.  # and associate a connection with the context.
  # blank line
    """  # """
  # blank line
    # this callback is used to prevent an auto-migration from being generated  # # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema  # # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html  # # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):  # def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):  # if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]  # script = directives[0]
            if script.upgrade_ops.is_empty():  # if script.upgrade_ops.is_empty():
                directives[:] = []  # directives[:] = []
                logger.info('No changes in schema detected.')  # logger.info('No changes in schema detected.')
  # blank line
    conf_args = current_app.extensions['migrate'].configure_args  # conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:  # if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives  # conf_args["process_revision_directives"] = process_revision_directives
  # blank line
    connectable = get_engine()  # connectable = get_engine()
  # blank line
    with connectable.connect() as connection:  # with connectable.connect() as connection:
        context.configure(  # context.configure(
            connection=connection,  # connection=connection,
            target_metadata=get_metadata(),  # target_metadata=get_metadata(),
            **conf_args  # **conf_args
        )  # )
  # blank line
        with context.begin_transaction():  # with context.begin_transaction():
            context.run_migrations()  # context.run_migrations()
  # blank line
  # blank line
if context.is_offline_mode():  # if context.is_offline_mode():
    run_migrations_offline()  # run_migrations_offline()
else:  # else:
    run_migrations_online()  # run_migrations_online()
