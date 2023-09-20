//SPDX-License-Identifier: UNLICENSED
pragma solidity >=0.8.0;

contract Marketplace {
  struct Nft {
    string name;
    string description;
    uint price;
    address payable seller;
    address owner;
    bool sold;
  }
  Nft[] public nfts;
  function addNft(string memory name, string memory description, uint price) public {
    nfts.push(Nft(name, description, price, payable(msg.sender), msg.sender, false));
  }
  function buyNft(uint nftId) public payable {
    Nft storage nft = nfts[nftId];
    require(!nft.sold, "product sold");
    require(msg.sender.balance > 0, "insufficient funds");
    nft.sold = true;
    nft.seller.transfer(msg.value);
    nft.owner = msg.sender;
  }
}