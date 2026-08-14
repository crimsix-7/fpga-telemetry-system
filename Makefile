# ============================================================
# Virtual CubeSat - Simulation / Regression Makefile
# ============================================================

SIM ?= verilator
TOPLEVEL_LANG ?= verilog

TEST ?= system


# ============================================================
# Select DUT and test
# ============================================================

ifeq ($(TEST),counter)

VERILOG_SOURCES = $(PWD)/rtl/telemetry_top.v
COCOTB_TOPLEVEL = telemetry_top
COCOTB_TEST_MODULES = test_telemetry

endif


ifeq ($(TEST),packetizer)

VERILOG_SOURCES = $(PWD)/rtl/telemetry_packetizer.v
COCOTB_TOPLEVEL = telemetry_packetizer
COCOTB_TEST_MODULES = test_packetizer

endif


ifeq ($(TEST),crc)

VERILOG_SOURCES = $(PWD)/rtl/crc16.v
COCOTB_TOPLEVEL = crc16
COCOTB_TEST_MODULES = test_crc16

endif


ifeq ($(TEST),uart)

VERILOG_SOURCES = $(PWD)/rtl/uart_tx.v
COCOTB_TOPLEVEL = uart_tx
COCOTB_TEST_MODULES = test_uart_tx

endif


ifeq ($(TEST),faults)

VERILOG_SOURCES = $(PWD)/rtl/fault_manager.v
COCOTB_TOPLEVEL = fault_manager
COCOTB_TEST_MODULES = test_fault_manager

endif


ifeq ($(TEST),system)

VERILOG_SOURCES = \
	$(PWD)/rtl/fault_manager.v \
	$(PWD)/rtl/telemetry_packetizer.v \
	$(PWD)/rtl/crc16.v \
	$(PWD)/rtl/uart_tx.v \
	$(PWD)/rtl/telemetry_system.v

COCOTB_TOPLEVEL = telemetry_system
COCOTB_TEST_MODULES = test_telemetry_system

endif


# ============================================================
# Python test path
# ============================================================

export PYTHONPATH := $(PWD)/tests:$(PWD):$(PYTHONPATH)


# ============================================================
# Waveform generation
# ============================================================

EXTRA_ARGS += --trace --trace-fst --trace-structs


# ============================================================
# Cocotb build system
# ============================================================

include $(shell cocotb-config --makefiles)/Makefile.sim


# ============================================================
# Full regression
# ============================================================

.PHONY: regression python-tests


python-tests:

	pytest tests/test_ground_station.py -v


regression:

	@echo ""
	@echo "========================================"
	@echo "Running Counter Verification"
	@echo "========================================"
	$(MAKE) clean
	$(MAKE) TEST=counter

	@echo ""
	@echo "========================================"
	@echo "Running Packetizer Verification"
	@echo "========================================"
	$(MAKE) clean
	$(MAKE) TEST=packetizer

	@echo ""
	@echo "========================================"
	@echo "Running CRC Verification"
	@echo "========================================"
	$(MAKE) clean
	$(MAKE) TEST=crc

	@echo ""
	@echo "========================================"
	@echo "Running UART Verification"
	@echo "========================================"
	$(MAKE) clean
	$(MAKE) TEST=uart

	@echo ""
	@echo "========================================"
	@echo "Running Fault Manager Verification"
	@echo "========================================"
	$(MAKE) clean
	$(MAKE) TEST=faults

	@echo ""
	@echo "========================================"
	@echo "Running Integrated System Verification"
	@echo "========================================"
	$(MAKE) clean
	$(MAKE) TEST=system

	@echo ""
	@echo "========================================"
	@echo "Running Ground Station Tests"
	@echo "========================================"
	pytest tests/test_ground_station.py -v

	@echo ""
	@echo "========================================"
	@echo "ALL REGRESSION TESTS COMPLETED"
	@echo "========================================"