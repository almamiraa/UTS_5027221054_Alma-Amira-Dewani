from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sys
sys.path.append('../')
import grpc
import menu_pb2
import menu_pb2_grpc
import os

app = Flask(__name__) 
CORS(app)

grpc_channel = grpc.insecure_channel('localhost:50051')
grpc_stub = menu_pb2_grpc.OrderServiceStub(grpc_channel)

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend'))
app.template_folder = template_dir

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/addOrder", methods=['POST'])
def add_order():
    data = request.json
    order_items = []
    for item in data['items']:
        order_items.append(menu_pb2.MenuItem(id=item['id'], name=item['name'], quantity=item['quantity'], price=item['price']))
    order_request = menu_pb2.Order(id=data['id'], items=order_items)
    response = grpc_stub.AddOrder(order_request)
    return jsonify({"message": "Order added successfully"})


@app.route("/allOrders")
def get_all_orders():
    response = grpc_stub.GetAllOrders(menu_pb2.Empty())
    order_list = [{"id": order.id, "items": [{"id": item.id, "name": item.name, "quantity": item.quantity, "price": item.price} for item in order.items]} for order in response.orders]
    return jsonify({"orders": order_list})

@app.route("/order/<order_id>")
def get_order(order_id):
    response = grpc_stub.GetOrder(menu_pb2.OrderId(id=order_id))
    if response.id:
        order_data = {"id": response.id, "items": [{"id": item.id, "name": item.name, "quantity": item.quantity, "price": item.price} for item in response.items]}
        return jsonify(order_data)
    else:
        return jsonify({"message": "Order not found"}), 404
    
@app.route("/updateOrder/<order_id>", methods=['PUT'])
def update_order(order_id):
    data = request.json
    order_items = []
    for item in data['items']:
        order_items.append(menu_pb2.MenuItem(id=item['id'], name=item['name'], quantity=item['quantity'], price=item['price']))
    order_request = menu_pb2.Order(id=order_id, items=order_items)
    response = grpc_stub.UpdateOrder(order_request)
    return jsonify({"message": "Order updated successfully"})


@app.route("/deleteOrder/<order_id>", methods=['DELETE'])
def delete_order(order_id):
    response = grpc_stub.DeleteOrder(menu_pb2.OrderId(id=order_id))
    return jsonify({"message": "Order deleted successfully"})


if __name__ == '__main__':
    app.run(debug=True)