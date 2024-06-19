import datetime
import click
from qstrader import settings
from qstrader.compat import queue
from qstrader.price_parser import PriceParser
from qstrader.price_handler.yahoo_daily_csv_bar import \
YahooDailyCsvBarPriceHandler
from kalman_qstrader_strategy import KalmanPairsTradingStrategy
from qstrader.position_sizer.naive import NaivePositionSizer
from qstrader.risk_manager.example import ExampleRiskManager
from qstrader.portfolio_handler import PortfolioHandler
from qstrader.compliance.example import ExampleCompliance
from qstrader.execution_handler.ib_simulated import \
IBSimulatedExecutionHandler
from qstrader.statistics.tearsheet import TearsheetStatistics
from qstrader.trading_session import TradingSession
from qstrader.strategy.base import Strategies

def run(config, testing, tickers, filename):
    # Set up variables needed for backtest
    events_queue = queue.Queue()
    csv_dir = config.CSV_DATA_DIR
    initial_equity = PriceParser.parse(100000.00)
    # Use Yahoo Daily Price Handler
    start_date = datetime.datetime(2009, 1, 2)
    end_date = datetime.datetime(2016, 12, 30)
    price_handler = YahooDailyCsvBarPriceHandler(
    csv_dir, events_queue, tickers,
    start_date=start_date, end_date=end_date
    )
    # Use the KalmanPairsTrading Strategy
    strategy = KalmanPairsTradingStrategy(tickers, events_queue)
    strategy = Strategies(strategy)

    # Use the Naive Position Sizer (suggested quantities are followed)
    position_sizer = NaivePositionSizer()
    # Use an example Risk Manager
    risk_manager = ExampleRiskManager()
    # Use the default Portfolio Handler
    portfolio_handler = PortfolioHandler(initial_equity, events_queue, price_handler,position_sizer, risk_manager)
    # Use the ExampleCompliance component
    compliance = ExampleCompliance(config)
    # Use a simulated IB Execution Handler
    execution_handler = IBSimulatedExecutionHandler(events_queue, price_handler, compliance)
    # Use the Tearsheet Statistics
    title = ["Kalman Filter Pairs Trade on TLT/IEI"]
    statistics = TearsheetStatistics(config, portfolio_handler, title)
    # Set up the backtest
    backtest = TradingSession(config, strategy, tickers,
        initial_equity, start_date, end_date, events_queue,
        session_type="backtest", end_session_time=None,
        price_handler = price_handler, portfolio_handler = portfolio_handler,
        compliance=compliance, position_sizer=position_sizer,
        execution_handler=execution_handler, risk_manager=risk_manager,
        statistics=statistics, sentiment_handler=None,
        title=title, benchmark=None)
    results = backtest.start_trading(testing=testing)
    statistics.save(filename)
    return results


@click.command()
@click.option('--config', default=settings.DEFAULT_CONFIG_FILENAME, help='Config filename')
@click.option('--tickers', help='Tickers (use comma)')
@click.option('--testing/--no-testing', default=False, help='Enable testing mode')
@click.option('--filename', default='', help='Pickle (.pkl) statistics filename')
def main(config, testing, tickers, filename):
    tickers = tickers.split(",")
    config = settings.from_file(config, testing)
    run(config, testing, tickers, filename)

if __name__ == "__main__":
    main()




