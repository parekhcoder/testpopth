from kubernetes import client, config, watch

# Load in-cluster Kubernetes config
config.load_incluster_config()
v1 = client.CoreV1Api()

def patch_pod(namespace, node_name, pod_name):
    """Patches the Pod by changing the PVC name dynamically and adding an annotation"""
    new_pvc_name = f"pvc-linstortest-{node_name}"  # Example: test-pvc-0-pvc

    patch_body = {
        "metadata": {
            "annotations": {
                "patched": "true"  # Mark Pod as patched
            }
        },
        "spec": {
            "volumes": [
                {
                    "name": "log-volume",
                    "persistentVolumeClaim": {
                        "claimName": new_pvc_name  # Change PVC reference
                    }
                }
            ]
        }
    }

    try:
        v1.patch_namespaced_pod(name=pod_name, namespace=namespace, body=patch_body)
        print(f"✅ Patched Pod {pod_name}: Updated PVC to {new_pvc_name}")
    except Exception as e:
        print(f"❌ Failed to patch Pod {pod_name}: {str(e)}")

NAMESPACE = "linstor-test"

def watch_scheduled_pods():
    """Watches for Pods that get scheduled and updates their PVC reference"""
    w = watch.Watch()
    for event in w.stream(v1.list_namespaced_pod, namespace=NAMESPACE, timeout_seconds=0):
        pod = event["object"]
        pod_name = pod.metadata.name
        namespace = pod.metadata.namespace
        node_name = pod.spec.node_name  # Only available after scheduling

        # Skip if Pod is not scheduled or already patched
        if not node_name or (pod.metadata.annotations and pod.metadata.annotations.get("patched") == "true"):
            continue

        print(f"📌 Pod {pod_name} scheduled on Node {node_name}, patching PVC...")
        patch_pod(namespace, node_name, pod_name)

if __name__ == "__main__":
    print("🚀 Watching for scheduled Pods...")
    watch_scheduled_pods()
