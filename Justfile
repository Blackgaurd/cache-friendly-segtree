# Dump disassembly for all seg-tree functions into asm/
asm:
    python3 tools/gen_asm.py

# Plot benchmark results from the last criterion run
plot:
    python3 tools/plot.py
