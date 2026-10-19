CC ?= cc
CFLAGS ?= -O3 -Wall
PYTHON ?= .venv/bin/python
PREFIX ?= $(HOME)/.local
BINDIR ?= $(PREFIX)/bin

.PHONY: all from-seed bootstrap stage1 stage2 stage3 test clean clean-bins install uninstall help

# Default target: Fast zero-dependency build from seed C amalgamation
all: bin/stkt-compiler

bin:
	mkdir -p bin build

bin/stkt-compiler: bin
	@if [ ! -f bootstrap/stkt.c ]; then \
		echo "bootstrap/stkt.c missing. Running full bootstrap..."; \
		$(MAKE) bootstrap; \
	else \
		echo "===> Compiling Stkt compiler from seed C amalgamation (bootstrap/stkt.c)..."; \
		$(CC) $(CFLAGS) bootstrap/stkt.c -o bin/stkt-compiler; \
		codesign -s - -f bin/stkt-compiler 2>/dev/null || true; \
		echo "✅ Built bin/stkt-compiler successfully!"; \
	fi

from-seed: bin
	$(CC) $(CFLAGS) bootstrap/stkt.c -o bin/stkt-compiler
	@codesign -s - -f bin/stkt-compiler 2>/dev/null || true
	@echo "✅ Built bin/stkt-compiler from seed!"

# Stage 1: Build compiler using Python reference implementation
bin/stage1_compiler: bin
	@echo "===> [Stage 1] Compiling Stkt compiler using Python reference..."
	$(PYTHON) src/stkt.py compiler/main.stkt -o bin/stage1_compiler
	@codesign -s - -f bin/stage1_compiler 2>/dev/null || true

stage1: bin/stage1_compiler

# Stage 2: Compile compiler using Stage 1
build/stage2.c bin/stage2_compiler: bin/stage1_compiler
	@echo "===> [Stage 2] Compiling Stkt compiler using Stage 1..."
	./bin/stage1_compiler compiler/main.stkt
	cp compiler/generated_output.c build/stage2.c
	$(CC) $(CFLAGS) build/stage2.c -o bin/stage2_compiler
	@codesign -s - -f bin/stage2_compiler 2>/dev/null || true

stage2: bin/stage2_compiler

# Stage 3: Compile compiler using Stage 2
build/stage3.c bin/stage3_compiler: bin/stage2_compiler
	@echo "===> [Stage 3] Compiling Stkt compiler using Stage 2..."
	./bin/stage2_compiler compiler/main.stkt
	cp compiler/generated_output.c build/stage3.c
	$(CC) $(CFLAGS) build/stage3.c -o bin/stage3_compiler
	@codesign -s - -f bin/stage3_compiler 2>/dev/null || true

stage3: bin/stage3_compiler

# Full 3-Stage Bootstrap Verification & Seed update
bootstrap: bin/stage3_compiler
	@echo "===> [Verification] Checking Stage 2 vs Stage 3 convergence..."
	@diff -u build/stage2.c build/stage3.c && echo "✅ BOOTSTRAP CONVERGED! Stage 2 and Stage 3 C outputs are 100% identical."
	@cp bin/stage3_compiler bin/stkt-compiler
	@cp bin/stage3_compiler compiler/self_compiler
	@mkdir -p bootstrap
	@cp build/stage3.c bootstrap/stkt.c
	@echo "===> Updated bootstrap/stkt.c seed and bin/stkt-compiler"

install: bin/stkt-compiler
	@echo "===> Installing stkt to $(BINDIR)..."
	@mkdir -p $(BINDIR)
	@cp bin/stkt-compiler $(BINDIR)/stkt
	@codesign -s - -f $(BINDIR)/stkt 2>/dev/null || true
	@echo "✅ Installed: $(BINDIR)/stkt"
	@echo "Make sure $(BINDIR) is in your PATH (e.g. export PATH=\"\$$HOME/.local/bin:\$$PATH\")"

uninstall:
	@echo "===> Uninstalling $(BINDIR)/stkt..."
	@rm -f $(BINDIR)/stkt
	@echo "✅ Uninstalled"

test:
	.venv/bin/pytest

clean:
	rm -rf bin build compiler/generated_output.c benchmarks/stkt_* benchmarks/rust_*

clean-bins:
	rm -f compiler/*_bin compiler/*_compiler compiler/main_out compiler/native_output compiler/*.c compiler/test_*
