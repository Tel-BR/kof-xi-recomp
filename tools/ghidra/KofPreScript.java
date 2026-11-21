import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.MemoryBlock;

public class KofPreScript extends GhidraScript {
    private static final long CODE_END = 0x00280830L;

    @Override
    public void run() throws Exception {
        println("=== KOF XI RECOMP: PRE-ANALYSIS BOUNDARY SETUP ===");
        MemoryBlock block = currentProgram.getMemory().getBlock(toAddr(0x00100000L));
        if (block != null && block.getEnd().getOffset() >= CODE_END) {
            println("Splitting memory block " + block.getName() + " at 0x" + Long.toHexString(CODE_END));
            currentProgram.getMemory().split(block, toAddr(CODE_END));
            
            MemoryBlock textBlock = currentProgram.getMemory().getBlock(toAddr(0x00100000L));
            textBlock.setName(".text");
            textBlock.setRead(true);
            textBlock.setWrite(false);
            textBlock.setExecute(true);

            MemoryBlock dataBlock = currentProgram.getMemory().getBlock(toAddr(CODE_END));
            dataBlock.setName(".data");
            dataBlock.setRead(true);
            dataBlock.setWrite(true);
            dataBlock.setExecute(false);
            println("Memory blocks configured: .text [0x100000-0x28082F] RX, .data [0x280830-0x2F13FF] RW");
        } else {
            println("Block already split or not found.");
        }
    }
}
