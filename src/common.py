"""
Модуль common содержит вспомогательные функции и классы.
"""

from exceptions import BadValidation
from schemas import DocumentShow, DocumentData, UserShow
from models import UserORM


class DocumentsID:
    """
    Класс содержит id типов документов

    PASSPORT_ID = 1

    POLIS_ID = 2

    SNILS_ID = 3

    INN_ID = 4
    """

    PASSPORT_ID = 1
    POLIS_ID = 2
    SNILS_ID = 3
    INN_ID = 4


def validate_document(document: DocumentData, type_id: int):
    """
    Функция проверки обязательных полей в зависимости от документа.
    :param document: объект класса DocumentData. Данные документа.
    :param type_id: тип int. Id типа документа.
    В случае ошибки выбразывается исключение, с описанием проблемы.
    """
    match type_id:
        case DocumentsID.PASSPORT_ID:
            if (
                document.series is not None
                and document.beginDate is not None
                and document.orgDep_Name is not None
            ):
                pass
            else:
                raise BadValidation(
                    f"Неверный формат документа {document.id}. Проверьте поля beginData, orgDep_Name, series."
                )
        case DocumentsID.POLIS_ID:
            if document.series is not None and document.orgDep_Name is not None:
                pass
            else:
                raise BadValidation(
                    f"Неверный формат документа {document.id}. Проверьте поля orgDep_Name, series."
                )
        case DocumentsID.SNILS_ID | DocumentsID.INN_ID:
            pass
        case _:
            raise BadValidation(f"Неверный тип документа {document.id}. ")


def create_user_show(user: UserORM):
    """
    Функция для преобразования orm модели пользователя, в pydantic модель для отправки в качестве ответа на запрос.
    :param user: объект класса UserORM.
    :return UserShow: объект класса UserShow
    """
    documents = user.documents
    list_of_documents = []
    for document in documents:
        if document.deleted == 0:
            document_show = DocumentShow(
                id=document.id,
                type_id=document.type_id,
                data=DocumentData.model_validate_json(document.data),
            )
            list_of_documents.append(document_show)
    user_show = UserShow(
        id=user.id,
        lastName=user.last_name,
        firstName=user.first_name,
        patrName=user.patr_name,
        gender_id=user.gender_id,
        type_id=user.type_id,
        documents=list_of_documents,
    )
    return user_show
