import psycopg2
from flask import Flask, request, jsonify
app = Flask(__name__)


# Connect to your database
connection = psycopg2.connect(
    host="localhost",
    database="rule_engine_db",
    user="postgres",  # Replace with your PostgreSQL username
    password="password"  # Replace with your PostgreSQL password
)

#/////
class Node:
    def __init__(self, type, left=None, right=None, value=None):
        self.type = type  # "operator" (AND/OR) or "operand" (conditions)
        self.left = left  # Left child node
        self.right = right  # Right child node
        self.value = value  # Operand condition (e.g., age > 30)
# Create a sample rule: age > 30 AND department = 'Sales'
node1 = Node(type="operand", value="age > 30")
node2 = Node(type="operand", value="department = 'Sales'")
root = Node(type="operator", left=node1, right=node2, value="AND")

# Print the structure
print(f"Root: {root.type} ({root.value})")
print(f"Left child: {root.left.type} ({root.left.value})")
print(f"Right child: {root.right.type} ({root.right.value})")

#///////
def create_rule(rule_string: str) -> Node:
    # Simple parsing for "age > 30 AND department = 'Sales'"
    if "AND" in rule_string:
        parts = rule_string.split(" AND ")
        left = Node(type="operand", value=parts[0])
        right = Node(type="operand", value=parts[1])
        root = Node(type="operator", left=left, right=right, value="AND")
        return root
rule = "age > 30 AND department = 'Sales'"
ast = create_rule(rule)
print(f"Parsed AST: {ast.type} ({ast.value})")
print(f"Left: {ast.left.value}")
print(f"Right: {ast.right.value}")

#//////
def store_ast_in_db(node: Node):
    cursor = connection.cursor()
    
    # Insert the node
    cursor.execute(
        "INSERT INTO ast_nodes (type, value) VALUES (%s, %s) RETURNING node_id",
        (node.type, node.value)
    )
    node_id = cursor.fetchone()[0]
    
    # Store left and right nodes
    if node.left:
        left_id = store_ast_in_db(node.left)
        cursor.execute("UPDATE ast_nodes SET left_node_id = %s WHERE node_id = %s", (left_id, node_id))
    
    if node.right:
        right_id = store_ast_in_db(node.right)
        cursor.execute("UPDATE ast_nodes SET right_node_id = %s WHERE node_id = %s", (right_id, node_id))

    connection.commit()
    return node_id
rule = "age > 30 AND department = 'Sales'"
ast = create_rule(rule)
root_node_id = store_ast_in_db(ast)
print(f"Stored AST with root node ID: {root_node_id}")
#//////

@app.route('/create_rule', methods=['POST'])
def evaluate_rule():
    try:
        # Parse JSON data from the request
        data = request.get_json()
        if not data:
            return "Bad Request: No JSON data found", 400
        
        # Process the data (this is where your rule evaluation would go)
        # For example:
        age = data.get('age')
        department = data.get('department')
        salary = data.get('salary')
        experience = data.get('experience')

        # Example return
        return jsonify({"message": "Data processed successfully", "data": data})
    
    except Exception as e:
        return f"Failed to decode JSON object: {str(e)}", 400

if __name__ == '__main__':
    app.run(debug=True)


# Test the connection
cursor = connection.cursor()
cursor.execute("SELECT version();")
db_version = cursor.fetchone()
print(f"Connected to PostgreSQL database version: {db_version}")



# Close the connection
cursor.close()
connection.close()