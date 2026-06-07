# Roadmap — v2+

## Planned Features

### Obsidian Vault Integration
**Status**: In progress

RTK v2 will support persistent cross-session memory via Obsidian vaults.

The `setup_memory.py` script initializes the vault structure.
Run it once per machine:

```bash
python setup_memory.py
```

This creates:
- `~/.rtk/memory/agent_memory.md` — persistent context
- `~/.rtk/memory/evolution_log.md` — track improvements
- `~/.rtk/memory/strategy.md` — current strategy

### APEX AGI Compatibility

RTK v2 is designed to work with APEX AGI self-evolution systems.
When both are active:
- RTK compresses tool output (context optimization)
- APEX AGI handles strategic reasoning and self-improvement

Learn more: https://github.com/hernandez42/apex-fusion
