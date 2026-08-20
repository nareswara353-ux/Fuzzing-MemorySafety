#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Constants.h"
#include "llvm/IRReader/IRReader.h"
#include "llvm/Support/SourceMgr.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/FileSystem.h"

#include <iostream>
#include <set>
#include <string>
#include <system_error>

using namespace llvm;

int main(int argc, char **argv) {
    if (argc < 2) {
        errs() << "Usage: " << argv[0] << " <target_bitcode.bc>\n";
        return 1;
    }

    LLVMContext Context;
    SMDiagnostic Err;
    std::unique_ptr<Module> M = parseIRFile(argv[1], Err, Context);

    if (!M) {
        Err.print(argv[0], errs());
        return 1;
    }

    std::set<uint64_t> extracted_integers;
    std::set<std::string> extracted_hex_tokens;

    outs() << "[*] [LLVM IR Analyzer] Analyzing Module: " << M->getName() << "\n";

    for (Function &F : *M) {
        if (F.isDeclaration()) continue;

        for (BasicBlock &BB : F) {
            for (Instruction &I : BB) {
                // 1. Tangkap Instruksi Integer Comparison (ICmpInst)
                if (auto *cmp = dyn_cast<ICmpInst>(&I)) {
                    for (unsigned i = 0; i < cmp->getNumOperands(); ++i) {
                        if (auto *CI = dyn_cast<ConstantInt>(cmp->getOperand(i))) {
                            uint64_t val = CI->getZExtValue();
                            extracted_integers.insert(val);

                            if (CI->getBitWidth() >= 8 && CI->getBitWidth() <= 64) {
                                char buf[32];
                                snprintf(buf, sizeof(buf), "0x%llX", (unsigned long long)val);
                                extracted_hex_tokens.insert(std::string(buf));
                            }
                        }
                    }
                }
                // 2. Tangkap Instruksi Switch-Case (SwitchInst)
                else if (auto *sw = dyn_cast<SwitchInst>(&I)) {
                    for (auto Case : sw->cases()) {
                        uint64_t val = Case.getCaseValue()->getZExtValue();
                        extracted_integers.insert(val);
                    }
                }
            }
        }
    }

    // Tulis hasil ke extracted_constraints.json
    std::error_code EC;
    raw_fd_ostream Out("extracted_constraints.json", EC, sys::fs::OF_Text);
    if (!EC) {
        Out << "{\n";
        Out << "  \"target_module\": \"" << M->getName() << "\",\n";
        Out << "  \"extracted_integers\": [";
        bool first = true;
        for (auto val : extracted_integers) {
            if (!first) Out << ", ";
            Out << val;
            first = false;
        }
        Out << "],\n";
        Out << "  \"hex_tokens\": [";
        first = true;
        for (const auto &hex : extracted_hex_tokens) {
            if (!first) Out << ", ";
            Out << "\"" << hex << "\"";
            first = false;
        }
        Out << "]\n";
        Out << "}\n";
        Out.close();
        outs() << "[+] [LLVM Analyzer] Successfully exported constraints to extracted_constraints.json\n";
    } else {
        errs() << "[-] Error writing JSON output: " << EC.message() << "\n";
        return 1;
    }

    return 0;
}