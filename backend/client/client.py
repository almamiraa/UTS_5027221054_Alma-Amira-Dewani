import grpc
import sys
sys.path.append('../')
import menu_pb2
import menu_pb2_grpc

def create_order(stub):
    order_id = input("Enter order ID: ")
    item_name = input("Enter item name: ")
    quantity = int(input("Enter item quantity: "))
    price = float(input("Enter item price: "))
    
    item = menu_pb2.MenuItem(name=item_name, quantity=quantity, price=price)
    order = menu_pb2.Order(id=order_id, items=[item])
    response = stub.AddOrder(order)
    print("AddOrder Response:", response)

def get_all_orders(stub):
    all_orders = stub.GetAllOrders(menu_pb2.Empty())
    print("GetAllOrders Response:", all_orders)

def get_order(stub):
    order_id = input("Enter order ID: ")
    order = stub.GetOrder(menu_pb2.OrderId(id=order_id))
    print("GetOrder Response:", order)

def update_order(stub):
    order_id = input("Enter order ID to update: ")
    item_name = input("Enter updated item name: ")
    quantity = int(input("Enter updated item quantity: "))
    price = float(input("Enter updated item price: "))
    
    item = menu_pb2.MenuItem(name=item_name, quantity=quantity, price=price)
    order = menu_pb2.Order(id=order_id, items=[item])
    response = stub.UpdateOrder(order)
    print("UpdateOrder Response:", response)

def delete_order(stub):
    order_id = input("Enter order ID to delete: ")
    response = stub.DeleteOrder(menu_pb2.OrderId(id=order_id))
    print("DeleteOrder Response:", response)

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = menu_pb2_grpc.OrderServiceStub(channel)

    while True:
        print("\n1. Add Order\n2. Get All Orders\n3. Get Order\n4. Update Order\n5. Delete Order\n6. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            create_order(stub)
        elif choice == '2':
            get_all_orders(stub)
        elif choice == '3':
            get_order(stub)
        elif choice == '4':
            update_order(stub)
        elif choice == '5':
            delete_order(stub)
        elif choice == '6':
            break
        else:
            print("Invalid choice! Please enter a valid option.")


if __name__ == '__main__':
    run()
