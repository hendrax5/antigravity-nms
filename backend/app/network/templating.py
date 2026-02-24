import os
from jinja2 import Environment, FileSystemLoader

# Path to the directory where Jinja2 templates are stored
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

# Ensure the template directory exists
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# Initialize the Jinja2 Environment
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), trim_blocks=True, lstrip_blocks=True)

def render_template(template_name: str, context: dict) -> str:
    """
    Renders a Jinja2 template with the provided context variables.
    """
    template = env.get_template(template_name)
    return template.render(**context)

def save_template(template_name: str, template_content: str):
    """
    Utility to programmatically create or update a Jinja2 template on disk.
    """
    file_path = os.path.join(TEMPLATE_DIR, template_name)
    with open(file_path, "w") as f:
        f.write(template_content)

# Pre-populate some base templates if they don't exist
bgp_cisco_template = """
router bgp {{ local_as }}
 bgp router-id {{ router_id }}
 {% for neighbor in neighbors %}
 neighbor {{ neighbor.ip }} remote-as {{ neighbor.remote_as }}
 {% if neighbor.description %}
 neighbor {{ neighbor.ip }} description {{ neighbor.description }}
 {% endif %}
 {% endfor %}
"""
if not os.path.exists(os.path.join(TEMPLATE_DIR, "bgp_cisco.j2")):
    save_template("bgp_cisco.j2", bgp_cisco_template)

vlan_cisco_template = """
{% for vlan in vlans %}
vlan {{ vlan.id }}
 name {{ vlan.name }}
{% endfor %}
"""
if not os.path.exists(os.path.join(TEMPLATE_DIR, "vlan_cisco.j2")):
    save_template("vlan_cisco.j2", vlan_cisco_template)
