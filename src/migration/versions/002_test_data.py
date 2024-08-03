"""002_test_data

Revision ID: 16bcd4a58f18
Revises: f63b7a4e867b
Create Date: 2024-08-03 18:52:35.855569

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "16bcd4a58f18"
down_revision: Union[str, None] = "f63b7a4e867b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
INSERT INTO users VALUES
(1, 'Админ', '', '', NULL, NULL, 'admin', 'QWRtaW4=', '2024-02-09 00:00:00', 1, NULL, NULL, 0);
    

INSERT INTO document_types VALUES
(1, 'Паспорт', '2024-02-09 00:00:00', 1, NULL, NULL, 0),
(2, 'Полис', '2024-02-09 00:00:00', 1, NULL, NULL, 0),
(3, 'СНИЛС', '2024-02-09 00:00:00', 1, NULL, NULL, 0),
(4, 'ИНН', '2024-02-09 00:00:00', 1, NULL, NULL, 0);

INSERT INTO user_types VALUES
(1, 'Администратор', '2024-02-09 00:00:00', 1, NULL, NULL, 0),
(2, 'Пользователь', '2024-02-09 00:00:00', 1, NULL, NULL, 0);

INSERT INTO gender_types VALUES
(1, 'Мужской', '2024-02-09 00:00:00', 1, NULL, NULL, 0),
(2, 'Женский', '2024-02-09 00:00:00', 1, NULL, NULL, 0);

UPDATE users SET gender_id=1,type_id=1 where id=1;
"""
    )


def downgrade() -> None:
    op.execute(
        """
    DELETE from document_types;
    DELETE from user_types;
    DELETE from gender_types; 
    DELETE from users;         
"""
    )
