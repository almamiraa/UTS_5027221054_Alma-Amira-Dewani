import grpc
import logging
import pymongo
import sys
sys.path.append('../')
from concurrent import futures
import menu_pb2
import menu_pb2_grpc

class OrderService(menu_pb2_grpc.OrderServiceServicer):
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["RestaurantOrders"]
        self.collection = self.db["Orders"]
        logging.info("Connected to MongoDB")

    def AddOrder(self, request, context):
        logging.info("Received AddOrder request: %s", request)
        order_data = {
            "id": request.id,
            "items": [{"id": item.id, "name": item.name, "quantity": item.quantity, "price": item.price} for item in request.items]
        }
        self.collection.insert_one(order_data)
        return request

    def GetAllOrders(self, request, context):
        logging.info("Received GetAllOrders request")
        order_list = []
        for order_data in self.collection.find():
            order = menu_pb2.Order(
                id=order_data["id"],
                items=[menu_pb2.MenuItem(id=item["id"], name=item["name"], quantity=item["quantity"], price=item["price"]) for item in order_data["items"]]
            )
            order_list.append(order)
        return menu_pb2.OrderList(orders=order_list)
    
    def GetOrder(self, request, context):
        logging.info("Received GetOrder request for order ID: %s", request.id)
        order_data = self.collection.find_one({"id": request.id})
        if order_data:
            order = menu_pb2.Order(
                id=order_data["id"],
                items=[menu_pb2.MenuItem(id=item["id"], name=item["name"], quantity=item["quantity"], price=item["price"]) for item in order_data["items"]]
            )
            return order
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Order not found")
            return menu_pb2.Order()
        
    def UpdateOrder(self, request, context):
        logging.info("Received UpdateOrder request for order ID: %s", request.id)
        order_data = self.collection.find_one({"id": request.id})
        if order_data:
            updated_order_data = {
                "id": request.id,
                "items": [{"id": item.id, "name": item.name, "quantity": item.quantity, "price": item.price} for item in request.items]
            }
            self.collection.update_one({"id": request.id}, {"$set": updated_order_data})
            return menu_pb2.Order(id=request.id, items=request.items)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Order not found")
            return menu_pb2.Order()

    def DeleteOrder(self, request, context):
        logging.info("Received DeleteOrder request for order ID: %s", request.id)
        result = self.collection.delete_one({"id": request.id})
        if result.deleted_count > 0:
            return menu_pb2.Empty()
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Order not found")
            return menu_pb2.Empty()

def serve():
    logging.basicConfig(level=logging.INFO)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    menu_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("Listening on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
