from web3 import Web3
from roles_royce.applications.panic_button_app.config.config_builder import DAOStrategiesBuilder, DAO, Blockchain, \
    BalancerPosition, AuraPosition


def main():
    w3_eth = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))

    strategies_gnosis_dao_ethereum = DAOStrategiesBuilder(DAO.GnosisDAO,
                                                          Blockchain.Ethereum,
                                                          balancer=[BalancerPosition(position_id='test_id_1',
                                                                                     bpt_address='0xcfca23ca9ca720b6e98e3eb9b6aa0ffc4a5c08b9'),
                                                                    BalancerPosition(position_id='test_id_2',
                                                                                     bpt_address='0xde8c195aa41c11a0c4787372defbbddaa31306d2')])
    strategies_gnosis_dao_ethereum.build_json(w3_eth)


if __name__ == "__main__":
    main()
