from dotenv import load_dotenv
import os
from phases.main_graph import MainGraph

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("api_key")
    initial_state = {"task":"develop a snake game using pygame. sound effect is not required."}

    # MainGraph 실행
    main_graph = MainGraph(api_key, model_name="gpt-4o-mini", max_tokens=16000)
    main_graph.run(initial_state)