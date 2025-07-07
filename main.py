import sys
import traceback
from modules.gui_interface import main as gui_main

def main():
    """
    Função principal que inicia a interface gráfica com PyQt5.
    """
    try:
        print("Iniciando aplicação...")
        gui_main()
        print("Aplicação encerrada normalmente.")
    except Exception as e:
        print(f"Erro ao iniciar a aplicação: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()