require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.18",
};

module.exports = {
  networks: {
    hardhat: {
		chainId: 1,
        	blockGasLimit: 100_000_000_000
    }
  }
}
