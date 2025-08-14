from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# このファイルをプロジェクトのパスに追加
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# プロジェクトの設定と環境変数をインポート
from dotenv import load_dotenv
load_dotenv()

# データベース設定と基底クラスをインポート
from app.database import Base
from app.database import DATABASE_URL

# Alembicの設定ファイルからロギング設定を読み込む
config = context.config

# 設定ファイルからロギング設定を行う（オプション）
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# メタデータのターゲットを設定
target_metadata = Base.metadata

# マイグレーションスクリプトのコンテキストを設定
def run_migrations_offline():
    """コマンドラインからマイグレーションを実行"""
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """アプリケーションから直接マイグレーションを実行"""
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = DATABASE_URL
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()