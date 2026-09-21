import 'wallet_state.dart';

class WalletController {
  WalletState state = const WalletState();
  void beginLoad() => state = const WalletState(loading: true);
  void fail(String message) => state = WalletState(error: message);
}
