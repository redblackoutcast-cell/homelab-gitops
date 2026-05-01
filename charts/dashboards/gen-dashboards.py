#!/usr/bin/env python3
"""Generates Grafana dashboard ConfigMap YAMLs for the homelab GitOps repo."""
import json

DS = {"type": "prometheus", "uid": "${datasource}"}

DS_VAR = {
    "name": "datasource", "type": "datasource", "query": "prometheus",
    "current": {}, "hide": 0, "includeAll": False, "label": "Datasource", "refresh": 1
}

def dashboard(title, uid, panels):
    return {
        "title": title, "uid": uid, "schemaVersion": 38, "version": 1,
        "refresh": "30s", "time": {"from": "now-6h", "to": "now"},
        "timezone": "Europe/London",
        "templating": {"list": [DS_VAR]},
        "panels": panels, "links": []
    }

def row(id, title, y):
    return {"id": id, "title": title, "type": "row", "collapsed": False,
            "gridPos": {"x": 0, "y": y, "w": 24, "h": 1}, "panels": []}

def stat(id, title, expr, unit, x, y, w, h, legend="", thresholds=None, color_mode="background"):
    return {
        "id": id, "title": title, "type": "stat", "datasource": DS,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "options": {
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "colorMode": color_mode, "graphMode": "none",
            "justifyMode": "auto", "orientation": "auto", "textMode": "auto"
        },
        "fieldConfig": {
            "defaults": {
                "unit": unit, "mappings": [],
                "thresholds": thresholds or {
                    "mode": "absolute",
                    "steps": [{"color": "green", "value": None},
                              {"color": "yellow", "value": 70},
                              {"color": "red", "value": 90}]
                }
            },
            "overrides": []
        },
        "targets": [{"datasource": DS, "expr": expr, "instant": True,
                     "legendFormat": legend, "refId": "A"}]
    }

def timeseries(id, title, targets, unit, x, y, w, h, fill=10, stacking="none"):
    return {
        "id": id, "title": title, "type": "timeseries", "datasource": DS,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "options": {
            "tooltip": {"mode": "multi", "sort": "desc"},
            "legend": {"displayMode": "table", "placement": "bottom",
                       "calcs": ["max", "mean", "lastNotNull"]},
            "stacking": {"mode": stacking}
        },
        "fieldConfig": {
            "defaults": {
                "unit": unit,
                "custom": {"lineWidth": 1, "fillOpacity": fill, "gradientMode": "opacity"}
            },
            "overrides": []
        },
        "targets": targets
    }

def t(expr, legend, ref="A"):
    return {"datasource": DS, "expr": expr, "legendFormat": legend, "refId": ref}

def bargauge(id, title, targets, unit, x, y, w, h, min_val=0, max_val=100):
    return {
        "id": id, "title": title, "type": "bargauge", "datasource": DS,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "options": {
            "reduceOptions": {"calcs": ["lastNotNull"]},
            "orientation": "horizontal", "displayMode": "gradient",
            "valueMode": "color"
        },
        "fieldConfig": {
            "defaults": {
                "unit": unit, "min": min_val, "max": max_val, "mappings": [],
                "thresholds": {
                    "mode": "percentage",
                    "steps": [{"color": "green", "value": None},
                              {"color": "yellow", "value": 70},
                              {"color": "red", "value": 90}]
                }
            },
            "overrides": []
        },
        "targets": targets
    }

def gauge(id, title, expr, unit, x, y, w, h, min_val=0, max_val=100, thresholds=None):
    return {
        "id": id, "title": title, "type": "gauge", "datasource": DS,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "options": {
            "reduceOptions": {"calcs": ["lastNotNull"]},
            "showThresholdLabels": False, "showThresholdMarkers": True
        },
        "fieldConfig": {
            "defaults": {
                "unit": unit, "min": min_val, "max": max_val, "mappings": [],
                "thresholds": thresholds or {
                    "mode": "percentage",
                    "steps": [{"color": "green", "value": None},
                              {"color": "yellow", "value": 70},
                              {"color": "red", "value": 90}]
                }
            },
            "overrides": []
        },
        "targets": [{"datasource": DS, "expr": expr, "instant": True,
                     "legendFormat": "", "refId": "A"}]
    }

# ── Dashboard 1: Proxmox Overview ────────────────────────────────────────────

GUEST_CPU   = 'pve_cpu_usage_ratio{id!~"node/.*"} * on(id) group_left(name) pve_guest_info * 100'
GUEST_MEM   = 'pve_memory_usage_bytes{id!~"node/.*"} * on(id) group_left(name) pve_guest_info'
GUEST_NETRX = 'rate(pve_network_receive_bytes{id!~"node/.*|storage/.*"}[5m]) * on(id) group_left(name) pve_guest_info'
GUEST_NETTX = 'rate(pve_network_transmit_bytes{id!~"node/.*|storage/.*"}[5m]) * on(id) group_left(name) pve_guest_info'
GUEST_DR    = 'rate(pve_disk_read_bytes{id!~"node/.*|storage/.*"}[5m]) * on(id) group_left(name) pve_guest_info'
GUEST_DW    = 'rate(pve_disk_write_bytes{id!~"node/.*|storage/.*"}[5m]) * on(id) group_left(name) pve_guest_info'

NO_THRESH   = {"mode": "absolute", "steps": [{"color": "text", "value": None}]}
GREEN_ONLY  = {"mode": "absolute", "steps": [{"color": "green", "value": None}]}

proxmox_panels = [
    row(1, "JBSRV01 Host", 0),
    stat(2, "Host CPU", 'pve_cpu_usage_ratio{id="node/JBSRV01"} * 100',
         "percent", 0, 1, 6, 4),
    stat(3, "Host Memory",
         'pve_memory_usage_bytes{id="node/JBSRV01"} / pve_memory_size_bytes{id="node/JBSRV01"} * 100',
         "percent", 6, 1, 6, 4),
    stat(4, "Host Uptime", 'pve_uptime_seconds{id="node/JBSRV01"}',
         "dtdurations", 12, 1, 6, 4, thresholds=GREEN_ONLY),
    stat(5, "Guests Online", 'count(pve_up{id!~"node/.*|storage/.*"} == 1)',
         "short", 18, 1, 6, 4, thresholds=GREEN_ONLY),

    row(6, "Guest Status", 5),
    bargauge(7, "Guest CPU %", [t(GUEST_CPU, "{{name}}")],
             "percent", 0, 6, 12, 8),
    bargauge(8, "Guest Memory Used", [t(GUEST_MEM, "{{name}}")],
             "bytes", 12, 6, 12, 8, min_val=0, max_val=16 * 1024**3),

    row(9, "CPU & Memory Over Time", 14),
    timeseries(10, "Guest CPU %",
               [t(GUEST_CPU, "{{name}}")],
               "percent", 0, 15, 12, 8),
    timeseries(11, "Guest Memory Used",
               [t(GUEST_MEM, "{{name}}")],
               "bytes", 12, 15, 12, 8),

    row(12, "Disk & Network I/O", 23),
    timeseries(13, "Disk Read",  [t(GUEST_DR, "{{name}}")], "Bps", 0,  24, 12, 8),
    timeseries(14, "Disk Write", [t(GUEST_DW, "{{name}}")], "Bps", 12, 24, 12, 8),
    timeseries(15, "Network Rx", [t(GUEST_NETRX, "{{name}}")], "Bps", 0,  32, 12, 8),
    timeseries(16, "Network Tx", [t(GUEST_NETTX, "{{name}}")], "Bps", 12, 32, 12, 8),

    row(17, "Proxmox Storage", 40),
    bargauge(18, "Storage Disk Usage",
             [t('pve_disk_usage_bytes{id=~"storage/.*"} / pve_disk_size_bytes{id=~"storage/.*"} * 100',
                "{{id}}")],
             "percent", 0, 41, 12, 6),
    bargauge(19, "Storage Free",
             [t('pve_disk_size_bytes{id=~"storage/.*"} - pve_disk_usage_bytes{id=~"storage/.*"}',
                "{{id}}")],
             "bytes", 12, 41, 12, 6, min_val=0, max_val=250 * 1024**3),
]

# ── Dashboard 2: NAS / ZFS ────────────────────────────────────────────────────

ARC_HIT_RATIO = (
    'node_zfs_arc_hits{hostname="JBNAS01"} / '
    '(node_zfs_arc_hits{hostname="JBNAS01"} + node_zfs_arc_misses{hostname="JBNAS01"})'
    ' * 100'
)

zfs_panels = [
    row(1, "ZFS Pool Health", 0),
    stat(2, "JBNAS_SSD",
         'node_zfs_zpool_state{hostname="JBNAS01", zpool="JBNAS_SSD", state="online"}',
         "short", 0, 1, 6, 4,
         thresholds={
             "mode": "absolute",
             "steps": [{"color": "red", "value": None}, {"color": "green", "value": 1}]
         }),
    stat(3, "JBNAS_MEDIA",
         'node_zfs_zpool_state{hostname="JBNAS01", zpool="JBNAS_MEDIA", state="online"}',
         "short", 6, 1, 6, 4,
         thresholds={
             "mode": "absolute",
             "steps": [{"color": "red", "value": None}, {"color": "green", "value": 1}]
         }),
    stat(4, "ARC Hit Ratio", ARC_HIT_RATIO,
         "percent", 12, 1, 6, 4,
         thresholds={
             "mode": "absolute",
             "steps": [{"color": "red", "value": None},
                       {"color": "yellow", "value": 70},
                       {"color": "green", "value": 90}]
         }),
    stat(5, "ARC Size",
         'node_zfs_arc_size{hostname="JBNAS01"}',
         "bytes", 18, 1, 6, 4, thresholds=GREEN_ONLY),

    row(6, "ZFS ARC Detail", 5),
    gauge(7, "ARC Utilisation",
          'node_zfs_arc_size{hostname="JBNAS01"} / node_zfs_arc_c_max{hostname="JBNAS01"} * 100',
          "percent", 0, 6, 8, 8),
    timeseries(8, "ARC Size vs Max",
               [t('node_zfs_arc_size{hostname="JBNAS01"}', "ARC Used"),
                t('node_zfs_arc_c_max{hostname="JBNAS01"}', "ARC Max", "B"),
                t('node_zfs_arc_c_min{hostname="JBNAS01"}', "ARC Min", "C")],
               "bytes", 8, 6, 16, 8),

    row(9, "ARC Hit/Miss Rate", 14),
    timeseries(10, "ARC Demand Hits / Misses",
               [t('rate(node_zfs_arc_demand_data_hits{hostname="JBNAS01"}[5m])', "Data Hits"),
                t('rate(node_zfs_arc_demand_data_misses{hostname="JBNAS01"}[5m])', "Data Misses", "B"),
                t('rate(node_zfs_arc_demand_metadata_hits{hostname="JBNAS01"}[5m])', "Meta Hits", "C"),
                t('rate(node_zfs_arc_demand_metadata_misses{hostname="JBNAS01"}[5m])', "Meta Misses", "D")],
               "ops", 0, 15, 24, 8),

    row(11, "NAS Host Resources", 23),
    timeseries(12, "NAS CPU %",
               [t('100 - (avg by (instance) (rate(node_cpu_seconds_total{instance="192.168.0.201",mode="idle"}[5m])) * 100)',
                  "CPU %")],
               "percent", 0, 24, 12, 8),
    timeseries(13, "NAS Memory",
               [t('node_memory_MemTotal_bytes{instance="192.168.0.201"} - node_memory_MemAvailable_bytes{instance="192.168.0.201"}',
                  "Used"),
                t('node_memory_MemTotal_bytes{instance="192.168.0.201"}', "Total", "B")],
               "bytes", 12, 24, 12, 8),
]

# ── Emit ConfigMap YAMLs ──────────────────────────────────────────────────────

def configmap(name, filename, db):
    db_json = json.dumps(db, indent=2)
    lines = [
        "apiVersion: v1",
        "kind: ConfigMap",
        "metadata:",
        f"  name: {name}",
        "  namespace: monitoring",
        "  labels:",
        '    grafana_dashboard: "1"',
        "data:",
        f"  {filename}: |",
    ]
    for line in db_json.splitlines():
        lines.append("    " + line)
    return "\n".join(lines) + "\n"

with open("charts/dashboards/proxmox-overview.yaml", "w") as f:
    f.write(configmap(
        "grafana-dashboard-proxmox-overview",
        "proxmox-overview.json",
        dashboard("Proxmox — Host & Guest Overview", "proxmox-overview", proxmox_panels)
    ))

with open("charts/dashboards/nas-zfs.yaml", "w") as f:
    f.write(configmap(
        "grafana-dashboard-nas-zfs",
        "nas-zfs.json",
        dashboard("NAS — ZFS Pools & ARC", "nas-zfs", zfs_panels)
    ))

print("Generated proxmox-overview.yaml and nas-zfs.yaml")
