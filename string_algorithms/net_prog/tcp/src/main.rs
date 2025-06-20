mod tcp;
use tcp::{Quad, State};
use std::io;
use etherparse;
use std::collections::HashMap;
use std::collections::hash_map::Entry;
fn main() -> io::Result<()> {
    let nic = tun_tap::Iface::new("tun0", tun_tap::Mode::Tun)?;
    // 应该是定义一个数组
    let mut buf = [0u8; 1504];
    let mut connections: HashMap<Quad, State> = Default::default();
    loop {
        let nbytes=  nic.recv(&mut buf[..])?;
        // be = big endian.
        let flags = u16::from_be_bytes([buf[0], buf[1]]);
        // the  ip version
        let proto = u16::from_be_bytes([buf[2], buf[3]]);
        if proto != 0x0800 {
            println!("This packet is not from ipv4, ignore it!");
            continue;
        }
        match etherparse::Ipv4HeaderSlice::from_slice(&buf[4..nbytes]) {
            Ok(iph) => {
                let src = iph.source_addr();
                let dst = iph.destination_addr();
                let proto = iph.protocol();
                // 0x06 == tcp packet
                if proto != 0x06 {
                    continue;
                }
                match etherparse::TcpHeaderSlice::from_slice(&buf[4 + iph.slice().len() ..]) {
                    Ok(tcph) => {
                        eprintln!("{} -> {}: TCP to port {}", src, dst, tcph.destination_port());
                        let data_i = 4 + iph.slice().len() + tcph.slice().len();
                        match connections.entry(Quad{src:(src, tcph.source_port()), dst:(dst,tcph.destination_port())}) {
                            Entry::Occupied(mut c) => {
                                c.get_mut().on_packet(iph, tcph, &buf[data_i..nbytes]);
                            },
                            Entry::Vacant(e) => {
                                
                            }
                        }
                    }, 
                    Err(e) => {
                        eprintln!("Error parsing tcp header: {:?}", e);
                    }
                }
            },
            Err(e) => {
                eprintln!("Error parsing ipv4 header: {:?}", e);
            }
        }

        eprintln!("read {} bytes: {:x?}", nbytes, &buf[..nbytes]);
    }
    Ok(())
}