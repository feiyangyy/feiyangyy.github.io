use etherparse;
use std::collections::HashMap;
use std::net::{IpAddr, Ipv4Addr};
use std::io;
// prelude(序幕)
use std::io::prelude::*;
// the Quad definition
#[derive(Clone, Copy, Debug, Hash, Eq, PartialEq)]
pub struct Quad {
  pub src :(Ipv4Addr, u16),
  pub dst: (Ipv4Addr, u16)
}

pub enum State {
  Closed, // default state
  Listen, // wait for new connection and accept it if one's coming
  SynRcvd, // Recvd Syn, is able to establish a connection
  Estab, // connection established.
}

// impl the default trait for the state.
impl Default for State {
  fn default() -> Self{
    State::Listen
  }
}
// Add methods for State, State could be struct or enumerations.
impl State {
  pub fn on_packet<'a> (&mut self, iph: etherparse::Ipv4HeaderSlice<'a>, tcph: etherparse::TcpHeaderSlice<'a>, data: &'a [u8]) {
    // you can see that, ip addr is determined by ip-layer, and port is defined by tcp-layer, which is used to identify the 
    // the target connection.
    // You can image that, A:3555 ->B:10, C:400 -> B:10, they are different connections.
    println!("{}:{} -> {}:{}", iph.source_addr(), tcph.source_port(), iph.destination_addr(), tcph.destination_port());
  }
}

struct SendSequenceSpace {
  una: u32, // 最久未被响应的包
  nxt: u32, // 下一个序号, 用于新包传输
  wnd: u16, // 滑动窗口大小
  up: bool,  // URG 标志
  wl1: usize, // 上次窗口更新时，使用的序号
  wl2: usize, // 上次窗口更新时，被响应的序号
  iss: u32, // 初始序号
}

struct RecvSequenceSpace {
  nxt: u32, // RCV.NXT 下一个预期接受的序号
  wnd: u16, // RCV.WND 接受端晃动窗口大小, 当前接收端预期接受的数据大小
  up: bool, // 控制位 ??
  irs:u32, // 初始接受序号
}

pub struct Connection {
  state: State,
  // send 相关
  send: SendSequenceSpace,
  // recv 相关
  recv: RecvSequenceSpace,
  ip: etherparse::Ipv4Header,
  tcp: etherparse::TcpHeader
}

impl Connection {
  pub fn accept<'a> (
    nic:&mut tun_tap::Iface,
    iphs: etherparse::Ipv4HeaderSlice<'a>,
    tcphs: etherparse::TcpHeaderSlice<'a>,
    data: &'a [u8]
  ) -> io::Result<Option<Self>>{
    let mut buf =  [0u8; 1500]; // 1500 是以太网最大帧
    if !tcphs.syn() {
      println!("not syn packet");
      return Ok(None);
    }

    let iss = 0;
    let wnd = 10;
    let mut c = Connection {
      state: State::SynRcvd, 
      // 这里简写iss 就是用同名iss 初始化, check that.
      send: SendSequenceSpace {iss, una: iss, nxt: 1, wnd: wnd, up: false, wl1: 0, wl2: 0 },
      recv: RecvSequenceSpace { irs: tcphs.sequence_number(), nxt: tcphs.sequence_number() + 1 , wnd: tcphs.window_size(), up: false },
      tcp: etherparse::TcpHeader::new(tcphs.source_port(), tcphs.destination_port(), iss, wnd),
      
    };


    Ok(None)
  }
}