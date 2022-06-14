import json
from abc import ABC

from graph.models.errors import VertexDoesNotExistError, EdgeDoesNotExistError
from graph.ngql.connection.connection import run_ngql
from graph.ngql.query.match import Limit, OrderBy
from graph.models.model_builder import ModelBuilder
from graph.ngql.record.edge import delete_edge_ngql
from graph.ngql.record.vertex import delete_vertex_ngql
from graph.ngql.statements.edge import EdgeDefinition


class Manager(ABC):
    def __init__(self):
        self.model = None

    def register(self, model):
        self.model = model


class BaseVertexManager(Manager):
    # def any(self, limit: Limit = Limit(10), order_by: OrderBy = None):
    #     return [
    #         item['v'] for item in ModelBuilder.match('(v)', {'v': self.model}, order_by=order_by, limit=limit)
    #     ]

    def get(self, vid: str | int):
        try:
            return list(
                ModelBuilder.match('(v)', {'v': self.model}, condition=f"id(v) == {json.dumps(vid)}", limit=Limit(1))
            )[0]['v']
        except IndexError:
            raise VertexDoesNotExistError(vid)

    def delete(self, vid_list: list[str, int], with_edge: bool = True):
        return run_ngql(delete_vertex_ngql(vid_list, with_edge))


class BaseEdgeManager(Manager):
    # def any(self, limit: Limit = Limit(10), order_by: OrderBy = None):
    #     return [
    #         item['e'] for item in ModelBuilder.match('()-[e]->()', {'e': self.model}, order_by=order_by, limit=limit)
    #     ]

    def get(self, edge_definition: EdgeDefinition):
        # TODO rank definition
        try:
            return list(
                ModelBuilder.match(
                    '(v1)-[e]->(v2)', {'e': self.model},
                    condition=f"id(v1) == {edge_definition.src_vid} "
                              f"AND id(v2) == {edge_definition.dst_vid}"
                    , limit=Limit(1)
                )
            )[0]['e']
        except IndexError:
            raise EdgeDoesNotExistError(edge_definition)

    def delete(self, edge_definitions: list[EdgeDefinition]):
        return run_ngql(delete_edge_ngql(self.model.get_edge_type_and_model()[1].db_name(), edge_definitions))
