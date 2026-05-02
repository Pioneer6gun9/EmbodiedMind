from __future__ import annotations
import json
from pathlib import Path
from embodiedmind.agents.perception_agent import PerceptionAgent
from embodiedmind.agents.planner_agent import PlannerAgent
from embodiedmind.agents.critic_agent import CriticAgent
from embodiedmind.agents.action_agent import ActionAgent
from embodiedmind.agents.reflection_agent import ReflectionAgent
from embodiedmind.dsl.executor import ActionExecutor
from embodiedmind.envs.tabletop_env import TabletopEnv
from embodiedmind.models.perception_model import ColorSegmentationModel
from embodiedmind.models.llm_client import RuleBasedLLMClient
from embodiedmind.utils.logger import RunLogger

class EmbodiedMindSystem:
    def __init__(self, task: dict, config: dict, run_dir: str | Path | None = None):
        env_cfg = config.get("env", {})
        robot_cfg = env_cfg.get("robot", {})
        self.env = TabletopEnv(
            task,
            seed=config.get("seed", 42),
            action_noise=robot_cfg.get("action_noise", 0.012),
            placement_noise=robot_cfg.get("placement_noise", 0.018),
        )
        agent_cfg = config.get("agents", {})
        self.perception = PerceptionAgent(
            ColorSegmentationModel(),
            confidence_threshold=agent_cfg.get("perception", {}).get("confidence_threshold", 0.65),
        )
        self.planner = PlannerAgent(RuleBasedLLMClient(), max_steps=agent_cfg.get("planner", {}).get("max_steps", 8))
        self.critic = CriticAgent(
            reach_radius=robot_cfg.get("reach_radius", 0.55),
            min_confidence=agent_cfg.get("critic", {}).get("min_object_confidence", 0.65),
        )
        self.action = ActionAgent(ActionExecutor(self.env))
        self.reflection = ReflectionAgent(max_replans=agent_cfg.get("reflection", {}).get("max_replans", 3))
        self.logger = RunLogger(run_dir)
        self.task = task

    def run_episode(self, randomize=True) -> dict:
        self.env.reset(randomize=randomize)
        obs = self.env.observe()
        state = self.perception.run(obs)
        self.logger.log("PerceptionAgent", f"detected objects: {', '.join(state.objects.keys())}")
        self.logger.log("WorldModel", json.dumps(state.to_compact_dict(), ensure_ascii=False)[:360] + "...")

        plan = self.planner.run(self.task["language_instruction"], state)
        self.logger.log("PlannerAgent", "plan: " + " -> ".join([a.name for a in plan]))

        steps = 0
        replans = 0
        violations = 0
        trace = []
        i = 0
        while i < len(plan) and steps < 16:
            action = plan[i]
            if action.name == "observe":
                state = self.perception.run(self.env.observe())
                self.logger.log("PerceptionAgent", "world state refreshed")
                i += 1; steps += 1
                continue

            validation = self.critic.validate(action, self.env.state)
            self.logger.log("CriticAgent", f"validated {action.name}({action.target}): {validation}")
            if not validation["valid"]:
                violations += 1
                if replans >= self.reflection.max_replans:
                    return {"success": False, "steps": steps, "replans": replans, "violations": violations}
                replans += 1
                diagnosis = self.reflection.diagnose(validation, self.env.state, trace)
                self.logger.log("ReflectionAgent", f"{diagnosis['diagnosis']}; strategy={diagnosis['strategy']}")
                plan = diagnosis["plan"] + plan[i+1:]
                i = 0
                continue

            result = self.action.run(action, self.env.state)
            trace.append({"action": action.model_dump(), "result": result})
            self.logger.log("ActionAgent", f"executed {action.name}({action.target}): {result}")
            steps += 1

            if not result.get("success", False):
                if replans >= self.reflection.max_replans:
                    return {"success": False, "steps": steps, "replans": replans, "violations": violations}
                replans += 1
                diagnosis = self.reflection.diagnose(result, self.env.state, trace)
                self.logger.log("ReflectionAgent", f"{diagnosis['diagnosis']}; local replan triggered")
                plan = diagnosis["plan"] + plan[i+1:]
                i = 0
                continue

            if self.env.is_success():
                self.logger.log("Task", "SUCCESS: red_block inside blue_box")
                return {"success": True, "steps": steps, "replans": replans, "violations": violations}
            i += 1

        success = self.env.is_success()
        self.logger.log("Task", "SUCCESS: red_block inside blue_box" if success else "FAILED")
        return {"success": success, "steps": steps, "replans": replans, "violations": violations}
