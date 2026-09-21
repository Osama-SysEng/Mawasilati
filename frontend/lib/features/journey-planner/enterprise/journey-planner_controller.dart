import 'journey-planner_state.dart';

class JourneyPlannerController {
  JourneyPlannerState state = const JourneyPlannerState();
  void beginLoad() => state = const JourneyPlannerState(loading: true);
  void fail(String message) => state = JourneyPlannerState(error: message);
}
