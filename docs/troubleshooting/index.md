# Troubleshooting

Common issues and solutions for DClaw Legal.

## Quick Diagnostics

```bash
# Check app pods
kubectl get pods -n dclaw-legal

# Check logs
kubectl logs -n dclaw-legal deployment/dclaw-legal-backend

# Check database
kubectl get clusters -n dclaw-legal
```

## Sections

- [Common Issues](./common-issues)
- [FAQ](./faq)
