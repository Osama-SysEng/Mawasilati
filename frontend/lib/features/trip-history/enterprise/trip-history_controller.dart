import 'trip-history_state.dart';

class TripHistoryController {
  TripHistoryState state = const TripHistoryState();
  void beginLoad() => state = const TripHistoryState(loading: true);
  void fail(String message) => state = TripHistoryState(error: message);
}
