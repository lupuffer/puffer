# Makefile — 钱学森问题扩展求解项目自动化构建
# ================================================
# 用法:
#   make all     : 一键生成所有图表、渲染动画、编译 report.pdf
#   make pdf     : 仅编译 report.pdf（快速目标）
#   make test    : 运行所有单元测试
#   make clean   : 清理所有生成文件
#   make figures : 仅生成静态图表
#   make cache   : 生成本地历表缓存
#
# 兼容: Windows (cmd.exe / PowerShell), Linux, macOS

.PHONY: all pdf test clean figures cache animate

# GnuWin32 make 默认用 MSYS bash，其中找不到 python。
# 强制所有 recipe 使用 cmd.exe，确保 python/del/if exist 等 Windows 命令可用。
SHELL = cmd.exe

NULL_DEV := nul
PYTHON   := python

# --- 主目标 ---

all: cache figures animate pdf
	@echo ""
	@echo "============================================"
	@echo "  ALL TARGETS COMPLETE"
	@echo "  - figures/ : static plots (PNG)"
	@echo "  - output/orbit_animation.mp4 : animation"
	@echo "  - report.pdf : final report"
	@echo "============================================"

pdf:
	@echo "Compiling report.tex with xelatex + biber (3-pass)..."
	-cd . && xelatex -interaction=nonstopmode report.tex
	-cd . && biber report
	-cd . && xelatex -interaction=nonstopmode report.tex
	-cd . && xelatex -interaction=nonstopmode report.tex
	@echo "  -> report.pdf generated."

test:
	@echo "Running Phase 1 tests..."
	cd src && $(PYTHON) nbody.py
	@echo ""
	@echo "Running Phase 2 tests..."
	cd src && $(PYTHON) horizons_verify.py --test-only
	@echo ""
	@echo "Running Phase 3 tests..."
	cd src && $(PYTHON) patched_conic.py
	@echo ""
	@echo "Running Phase 4 tests..."
	cd src && $(PYTHON) trajectory_optimizer.py --test-only
	@echo ""
	@echo "Running O3 tests (Newton-Raphson)..."
	cd src && $(PYTHON) differential_corrector.py
	@echo ""
	@echo "Running E2E tests (Rules 15-16)..."
	cd src && $(PYTHON) end_to_end_trajectory.py
	@echo ""
	@echo "Running Numerical Optimizer tests (Rule 11)..."
	cd src && $(PYTHON) numerical_optimizer.py
	@echo ""
	@echo "Running 3D extension tests (Rule 22)..."
	cd src && $(PYTHON) nbody_3d.py
	@echo ""
	@echo "Running Multi-flyby tests (Rule 24)..."
	cd src && $(PYTHON) multi_flyby.py
	@echo ""
	@echo "Running Parallel computing tests (Rule 27)..."
	cd src && $(PYTHON) parallel_computing.py
	@echo ""
	@echo "Running GA optimizer tests (Rule 27)..."
	cd src && $(PYTHON) ga_optimizer.py
	@echo ""
	@echo "============================================"
	@echo "  ALL TESTS COMPLETE"
	@echo "============================================"

# --- 子目标 ---

figures:
	@echo "Generating static plots..."
	cd src && $(PYTHON) plot_results.py

cache:
	@echo "Generating horizon cache..."
	cd src && $(PYTHON) generate_cache.py

animate:
	@echo "Rendering orbit animation (may take 5-10 min)..."
	@echo "  Note: requires ffmpeg on PATH; falls back to GIF if unavailable"
	cd src && $(PYTHON) plot_results.py --animate-only

# --- 清理 ---

clean:
	@echo "Cleaning generated files..."
	-del /q report.pdf 2>nul
	-del /q report.aux 2>nul
	-del /q report.log 2>nul
	-del /q report.out 2>nul
	-del /q report.toc 2>nul
	-del /q report.synctex.gz 2>nul
	-del /q report.bbl 2>nul
	-del /q report.blg 2>nul
	-del /q report.run.xml 2>nul
	-del /q report.bcf 2>nul
	-del /q report.fdb_latexmk 2>nul
	-del /q report.fls 2>nul
	-del /q figures\*.png 2>nul
	-del /q output\orbit_animation.mp4 2>nul
	-del /q output\orbit_animation.gif 2>nul
	-del /q output\horizons_verify\*.csv 2>nul
	@echo "  Clean complete."
