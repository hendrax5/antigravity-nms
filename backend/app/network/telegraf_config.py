import os
from sqlalchemy.orm import Session
from app.models.device import Device
from app.models.credential import CredentialProfile
import logging

logger = logging.getLogger(__name__)

# Assumes the backend container has this path mapped, or the script runs on the host.
# For Docker Compose, they share the directory or a volume.
TELEGRAF_CONF_PATH = os.environ.get("TELEGRAF_CONF_PATH", "/app/telegraf/telegraf.conf")

def generate_telegraf_config(db: Session):
    """
    Auto-generates the telegraf.conf based on active device inventory in PostgreSQL.
    Configures ICMP Ping and SNMP polling for each active device.
    """
    logger.info("Generating new telegraf.conf based on active inventory...")
    
    devices = db.query(Device).filter(Device.status == "active").all()
    
    ip_list_str = ", ".join([f'"{device.ip_address}"' for device in devices])
    
    config_lines = [
        '# AUTO-GENERATED CONFIGURATION BY ANTIGRAVITY NMS',
        '[global_tags]',
        '  project = "antigravity_nms"',
        '',
        '[agent]',
        '  interval = "10s"',
        '  round_interval = true',
        '  metric_batch_size = 1000',
        '  metric_buffer_limit = 10000',
        '  collection_jitter = "0s"',
        '  flush_interval = "10s"',
        '  flush_jitter = "0s"',
        '  precision = ""',
        '  hostname = "telegraf-agent"',
        '  omit_hostname = false',
        '',
        '[[outputs.influxdb]]',
        '  urls = ["http://influxdb:8086"]',
        '  database = "telegraf"',
        '  username = "admin"',
        '  password = "${INFLUXDB_PASSWORD}"',
        '',
        '## --- INTERNAL SENSORS (PING) ---',
        '[[inputs.ping]]',
        f'  urls = [{ip_list_str}]',
        '  count = 1',
        '  ping_interval = 1.0',
        '  timeout = 1.0'
    ]
    
    # SNMP block generation 
    config_lines.append('\n## --- SNMP SENSORS ---')
    for device in devices:
        # Check if the device has an SNMP community mapping or default to public
        # Using a dummy or default public string for generation (In Prod: DB Field required)
        community = "public"
        
        config_lines.extend([
            '[[inputs.snmp]]',
            f'  agents = ["{device.ip_address}:161"]',
            '  version = 2',
            f'  community = "{community}"',
            '  name = "snmp"',
            '',
            '  [inputs.snmp.tags]',
            f'    tenant_id = "{device.tenant_id}"',
            f'    device_id = "{device.id}"',
            f'    hostname = "{device.hostname}"',
            '',
            '  ## Hostname',
            '  [[inputs.snmp.field]]',
            '    name = "hostname"',
            '    oid = "RFC1213-MIB::sysName.0"',
            '    is_tag = true',
            '',
            '  ## Uptime',
            '  [[inputs.snmp.field]]',
            '    name = "uptime"',
            '    oid = "DISMAN-EXPRESSION-MIB::sysUpTimeInstance"',
            '',
            '  ## IF-MIB Data for Bandwidth',
            '  [[inputs.snmp.table]]',
            '    name = "interface"',
            '    inherit_tags = [ "hostname" ]',
            '    oid = "IF-MIB::ifTable"',
            '    [[inputs.snmp.table.field]]',
            '      name = "ifDescr"',
            '      oid = "IF-MIB::ifDescr"',
            '      is_tag = true',
            ''
        ])
        
    config_content = "\n".join(config_lines)
    
    try:
        # Optional: ensure directory exists if we are running locally
        os.makedirs(os.path.dirname(TELEGRAF_CONF_PATH), exist_ok=True)
        with open(TELEGRAF_CONF_PATH, "w") as f:
            f.write(config_content)
        logger.info(f"Successfully wrote {TELEGRAF_CONF_PATH}")
        return True
    except Exception as e:
        logger.error(f"Failed to write telegraf config: {str(e)}")
        return False
