#include "llvm/IR/PassManager.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Function.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Config/llvm-config.h"

#include <system_error>
#include <set>
#include <string>

using namespace llvm;

namespace {

struct BranchExtractorPass : public PassInfoMixin<BranchExtractorPass> {
    PreservedAnalyses run(Module &M, ModuleAnalysisManager &MAM) {
        std::set<uint64_t> extracted_integers;
        std::set<std::string> extracted_hex_tokens;

        outs() << "[*] [LLVM Pass] Analyzing Module: " << M.getName() << "\n";

        for (Function &F : M) {
            if (F.isDeclaration()) continue;

            for (BasicBlock &BB : F) {
                for (Instruction &I : BB) {
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
                    } else if (auto *sw = dyn_cast<SwitchInst>(&I)) {
                        for (auto Case : sw->cases()) {
                            uint64_t val = Case.getCaseValue()->getZExtValue();
                            extracted_integers.insert(val);
                        }
                    }
                }
            }
        }

        std::error_code EC;
        raw_fd_ostream Out("extracted_constraints.json", EC, sys::fs::OF_Text);
        if (!EC) {
            Out << "{\n";
            Out << "  \"target_module\": \"" << M.getName() << "\",\n";
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
            outs() << "[+] [LLVM Pass] Successfully exported constraints to extracted_constraints.json\n";
        }

        return PreservedAnalyses::all();
    }
};

} // end anonymous namespace

extern "C" ::llvm::PassPluginLibraryInfo LLVM_ATTRIBUTE_WEAK llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION,
        "BranchExtractorPass",
        LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, ModulePassManager &MPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "branch-extractor") {
                        MPM.addPass(BranchExtractorPass());
                        return true;
                    }
                    return false;
                });
        }
    };
}