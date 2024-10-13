from argparse import ArgumentParser

from src.brookshear.core import BrookshearMachine

parser = ArgumentParser(description="Brookshear Machine Simulator")
parser.add_argument("program", help="Machine code program file")
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
parser.add_argument("--step-by-step", action="store_true", help="Enable step-by-step mode")
args = parser.parse_args()

machine = BrookshearMachine()
machine.debug = args.debug

machine.open_program(args.program)

machine.run(step_by_step=args.step_by_step)
machine.show_registers()
machine.show_memory()
