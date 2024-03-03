#include <iostream>
#include <fstream>
#include <string>
#include <cassert>
#include <time.h>
#include "ns3/packet.h"
#include "ns3/netanim-module.h"
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/ipv4-static-routing-helper.h"
#include "ns3/ipv4-list-routing-helper.h"
#include "ns3/gnuplot.h"


using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("SocketBoundRoutingExample");

void SendStuff (Ptr<Socket> sock, Ipv4Address dstaddr, uint16_t port, struct parameters packetParameters);  //flag: 1 - Forward, 0 - Dummy
void BindSock (Ptr<Socket> sock, Ptr<NetDevice> netdev);
void socketRecv (Ptr<Socket> socket);
void Create2DPlotFile ();


struct parameters{
    uint8_t flags[5];
    uint8_t hopCount;
    uint32_t addresses[5];
    uint8_t packetData[12];
};

uint16_t port = 12345;
const int numberOfNodes = 100;
const int numberOfTestIteration = 100;
const int delayDataLength = numberOfTestIteration;
const int repeatDataLength = 50;
double delayData[delayDataLength][repeatDataLength];
int testIdx = 0;
int repeatIdx = 0;
int maxHopDelay = 100;
uint32_t keys[5];
std::chrono::high_resolution_clock::time_point sentTime;

uint32_t entryNode,intermediateNode,exitNode;

class ProposedHeader : public Header
{

    public:

        TypeId GetInstanceTypeId (void) const
        {
            static TypeId tid = TypeId ("ProposedHeader")
                                .SetParent<Header> ()
                                .AddConstructor<ProposedHeader> ()
                                ;
            return tid;
        }

        uint32_t GetSerializedSize (void) const
        {
            return 26;
        }

        void Serialize (Buffer::Iterator start) const
        {
            start.WriteU8(hopCount);
            uint32_t  i = 0;
            for(i = 0; i < 5; ++i)
            {
                start.WriteU8(FPFlag[i]);            //FP FLAG
                start.WriteU32(forwardAddress[i]);  //Forwarding Address
            }

        }

        uint32_t Deserialize (Buffer::Iterator start)
        {
            hopCount = start.ReadU8();
            for(uint32_t i = 0; i < 5; ++i)
            {
                FPFlag[i] = start.ReadU8();
                forwardAddress[i] = start.ReadU32();
            }

            return 26; // the number of bytes consumed.
        }

        void SetFlag(uint8_t flag, uint32_t index)
        {
            FPFlag[index] = flag;
        }

        void SetForwardAddress(uint32_t address, uint32_t index)
        {
            forwardAddress[index] = address;
        }
        
        void SetHopCount(uint32_t hop)
        {
            hopCount = hop;
        }

        void Print (std::ostream &os) const
        {
            os <<"Proposed Header Contents:\n---------------------------------------------\nHop Count: " <<  (uint32_t)hopCount << "\n";
            for(uint32_t i = 0; i < 5; ++i)
            {
                os << "\nFP Flag "<< i <<": "<< (uint32_t)FPFlag[i]
                << "\tForward Address "<< i <<": " << (forwardAddress[i]) <<"\n";
            }
            os << "\n---------------------------------------------\n";
        };
        uint8_t * GetFlags()
        {
            return FPFlag;
        }

        uint32_t * GetForwardAddresses()
        {
            return forwardAddress;
        }
        uint8_t GetHopCount()
        {
            return hopCount;
        }

    private:
        uint8_t FPFlag[5];  //1 - Forward
        uint32_t forwardAddress[5];
        uint8_t hopCount;
};

int main (int argc, char *argv[])
{
    CommandLine cmd;
    cmd.Parse (argc, argv);
    testIdx = 0;

    const int numberOfActiveSenders = 0.5*numberOfNodes;
    Ptr<Node> nPtr[numberOfActiveSenders];
    for(int i = 0; i < numberOfActiveSenders; i++) {
        nPtr[i] = CreateObject<Node> ();
    }

    NodeContainer c = NodeContainer (nPtr[0], nPtr[1], nPtr[2], nPtr[3], nPtr[4]);
    for(int i = 5; i < numberOfActiveSenders; i++)
        c.Add(nPtr[i]);

    InternetStackHelper internet;
    internet.Install (c);

    NodeContainer nC[numberOfActiveSenders][numberOfActiveSenders];

    for(int i = 0; i < numberOfActiveSenders; i++) {
        for(int j = i + 1; j < numberOfActiveSenders; j++) {
                nC[i][j] = NodeContainer (nPtr[i], nPtr[j]);
        }
    }

    PointToPointHelper p2p;
    p2p.SetDeviceAttribute ("DataRate", StringValue ("5Mbps"));
    p2p.SetChannelAttribute ("Delay", StringValue ("2ms"));

    NetDeviceContainer nDC[numberOfActiveSenders][numberOfActiveSenders];

    for(int i = 0; i < numberOfActiveSenders; i++) {
        for(int j = i + 1; j < numberOfActiveSenders; j++) {
                nDC[i][j] = p2p.Install(nC[i][j]);
        }
    }

    Ipv4AddressHelper ipv4;
    Ipv4InterfaceContainer nIC[numberOfActiveSenders][numberOfActiveSenders];
    for(int i = 0; i < numberOfActiveSenders; i++) {
        for(int j = i+1; j < numberOfActiveSenders; j++) {
            char *ip = new char[20];
            int max = 170;
            int min = 10;
            int range = max - min + 1;
            int firstOctetNumber = rand() % range + min;
            if(firstOctetNumber == 127 || firstOctetNumber == 128)
                firstOctetNumber = 120;
            int secondOctetNumber = rand() % range + min;
            int thirdOctetNumber = rand() % range + min;
            sprintf (ip, "%d.%d.%d.%d", firstOctetNumber, secondOctetNumber, thirdOctetNumber, 0);
            ipv4.SetBase(ip, "255.255.255.0");
            nIC[i][j] = ipv4.Assign(nDC[i][j]);
        }
    }

    Ipv4GlobalRoutingHelper::PopulateRoutingTables ();
    Ipv4Address addresses[numberOfActiveSenders];
    for(int i = 0; i < numberOfActiveSenders; i++) {
        addresses[i] = nPtr[i]->GetObject<Ipv4>()->GetAddress(1, 0).GetLocal();
    }

    Ptr<Socket> nSocket[numberOfActiveSenders];
    // InetSocketAddress nSocketAddr[numberOfActiveSenders];
    for(int i = 0; i < numberOfActiveSenders; i++) {
        nSocket[i] = Socket::CreateSocket(nPtr[i], TypeId::LookupByName ("ns3::UdpSocketFactory"));
        // nSocketAddr[i] = InetSocketAddress(addresses[i], port);
        InetSocketAddress nSocketAddr = InetSocketAddress(addresses[i], port);
        nSocket[i]->Bind(nSocketAddr);
        nSocket[i]->SetRecvCallback(MakeCallback (&socketRecv));
    }

    AsciiTraceHelper ascii;
    p2p.EnableAsciiAll (ascii.CreateFileStream ("socket-bound-static-routing.tr"));
    LogComponentEnable ("SocketBoundRoutingExample", LOG_LEVEL_INFO);

    srand(time(NULL));

    for(int it=1;it<=numberOfTestIteration;it++) {
        for(int jt=1;jt<=repeatDataLength;jt++) {
            maxHopDelay = it;
            struct parameters packetParameters;
            uint32_t i = 0;
            int32_t j;
            int max = numberOfActiveSenders;
            int min = 0;
            int range = max - min;
            uint32_t senderClusterPathLength = 1;
            uint32_t receiverClusterPathLength = 1;
            uint32_t relayClusterPathLength = 3;
            // uint32_t path[4];
            uint32_t senderClusterPath[2];
            uint32_t receiverClusterPath[2];
            uint32_t relayClusterPath[3];

            // cluster-#1: 
            //          Entities: [1,2,3,4,5,6,7,8,9,10,11,12]
            //          PRs: [13,14,15,16]
            max = 11;
            min = 0;
            range = max - min;
            int firstHop = rand() % range + min;
            senderClusterPath[0]=firstHop;

            for(i=0;i<senderClusterPathLength;i++){
                max = 15;
                min = 12;
                range = max - min;

                int nextHop = rand() % range + min;
                while(true) {
                    bool isExist = false;
                    for(int j=0;j<i+1;j++)
                        if(nextHop == senderClusterPath[j])
                            isExist = true;
                    
                    if(isExist)
                        nextHop = rand() % range + min;
                    else
                        break;
                }      
                senderClusterPath[i+1]=nextHop;
            }

            // cluster-#2: 
            //          Entities: [17,18,19,20,21,22,23,24,25,26,27,28,29,30]
            //          PRs: [31,32,33,34]
            max = 33;
            min = 16;
            range = max - min;
            for(i=0;i<relayClusterPathLength;i++){
                if((i == 0) || (i == (relayClusterPathLength-1))) {
                    max = 33;
                    min = 30;
                    range = max - min;
                } else {
                    max = 29;
                    min = 16;
                    range = max - min;
                }

                int nextHop = rand() % range + min;
                while(true) {
                    bool isExist = false;
                    for(int j=0;j<i;j++)
                        if(nextHop == relayClusterPath[j])
                            isExist = true;
                    
                    if(isExist)
                        nextHop = rand() % range + min;
                    else
                        break;
                }      
                relayClusterPath[i]=nextHop;
            }

            // cluster-#3: 
            //          Entities: [35,36,37,38,39,40,41,42,43,44,45,46]
            //          PRs: [47,48,49,50]
            for(i=0;i<receiverClusterPathLength+1;i++){
                if(i == 0) {
                    max = 49;
                    min = 46;
                    range = max - min;
                } else {
                    max = 45;
                    min = 34;
                    range = max - min;
                }

                int nextHop = rand() % range + min;
                while(true) {
                    bool isExist = false;
                    for(int j=0;j<i;j++)
                        if(nextHop == receiverClusterPath[j])
                            isExist = true;
                    
                    if(isExist)
                        nextHop = rand() % range + min;
                    else
                        break;
                }      
                receiverClusterPath[i]=nextHop;
            }

            printf("\n\n                 {N12-...-N15} -> {N30-...-N33}        {N30-...-N33} -> {N46-...-N49}\n"\
                   "Clusters:       /                             \\        /                             \\\n"\
                   "          {N1-...-N11}                      {N16-...-N29}                       {N34-...-N45}\n\n\n");
                   

            printf("\nIP Address:\n");
            for(uint32_t k = 0; k < numberOfActiveSenders; k++){
                NS_LOG_INFO("N" << k << "\t" << addresses[k]);
            }

            printf("\n\n                 Sender's-PR -> Relay's-PR       Relay's-PR -> Receiver's-PR\n"\
                   "Path:           /                         \\     /                           \\\n"\
                   "          sender                           Relay                             Receiver\n\n\n");
            printf("     N%d -> N%d      N%d -> N%d\n"\
                   "   /           \\   /           \\\n"\
                   "N%d             N%d              N%d\n",senderClusterPath[1],relayClusterPath[0],relayClusterPath[2],receiverClusterPath[0],
                                                                senderClusterPath[0],relayClusterPath[1],receiverClusterPath[1]);

            for(i = 0; i < senderClusterPathLength + relayClusterPathLength + receiverClusterPathLength; ++i) {
                keys[i] = (rand() % 100000000000) + 1;
                packetParameters.flags[i] = 1;
            }

            packetParameters.addresses[0] = addresses[relayClusterPath[0]].Get() - keys[0];
            packetParameters.addresses[1] = addresses[relayClusterPath[1]].Get() - keys[1];
            packetParameters.addresses[2] = addresses[relayClusterPath[2]].Get() - keys[2];
            packetParameters.addresses[3] = addresses[receiverClusterPath[0]].Get() - keys[3];
            packetParameters.addresses[4] = addresses[receiverClusterPath[1]].Get() - keys[4];

            // printf("\nEnter Packet Data to be sent (Upto 5 characters):\n");
            // std::cin >> packetParameters.packetData;

            memcpy(packetParameters.packetData, "Hello there!", 12);
            // packetParameters.packetData = "Hello there!";

            for(i = 0; i < 12; ++i){
                packetParameters.packetData[i] -= (keys[0] + keys[1] + keys[2] + keys[3] + keys[4]);
            }
            packetParameters.packetData[12] = '\0';
            packetParameters.hopCount = 0;

            Simulator::Schedule(Seconds(1), &SendStuff, nSocket[senderClusterPath[0]], addresses[senderClusterPath[1]], port, packetParameters);
            Simulator::Run();
        }
    }

    // Simulator::Run();
    Create2DPlotFile();
    Simulator::Destroy();

    return 0;
}


void SendStuff (Ptr<Socket> sock, Ipv4Address dstaddr, uint16_t port, struct parameters packetParameters)
{
    uint32_t size = 12;
    uint32_t i = 0;
    Address addr;
    sock->GetSockName (addr);
    InetSocketAddress iaddr = InetSocketAddress::ConvertFrom (addr);

    Packet p1(packetParameters.packetData, size);
    Ptr<Packet> p = p1.Copy();
    ProposedHeader proposedHeader;

    for(i = 0; i < 5; ++i)
    {
        proposedHeader.SetFlag(packetParameters.flags[i], i);
        if(packetParameters.flags[i] == 1)
            proposedHeader.SetForwardAddress(packetParameters.addresses[i], i);
        else
            proposedHeader.SetForwardAddress(0, i);
    }
    proposedHeader.SetHopCount(packetParameters.hopCount);

    p->AddHeader(proposedHeader);


    NS_LOG_INFO("\n" << iaddr.GetIpv4() << " Sending packet to: " << dstaddr);

    int hopCount = (int) (proposedHeader.GetHopCount());
    if(hopCount == 0) {
        // std::cout << "[*] Hop-Count: " << (int)(proposedHeader.GetHopCount()) << "\n";
        sentTime = std::chrono::high_resolution_clock::now();
    } 
    
    int max = maxHopDelay;
    int min = 1;
    int range = max - min + 1;
    int num = rand() % range + min;
    // std::cout << "[*]Random-Delay: " << num << ' ' << '\n'; // generate numbers
    
    std::this_thread::sleep_for(std::chrono::milliseconds(num));
    sock->SendTo (p, 0, InetSocketAddress (dstaddr,port));
    
    return;
}

void socketRecv (Ptr<Socket> socket)
{
    Address from;

    uint32_t size;
    uint8_t * tempFlags;
    uint32_t * tempAddr;
    uint32_t i = 0;

    struct parameters packetParameters;


    Ptr<Packet> packet = socket->RecvFrom (from);
    packet->RemoveAllPacketTags ();
    packet->RemoveAllByteTags ();

    NS_LOG_INFO ("" << "Received " << packet->GetSize () << " bytes from " << InetSocketAddress::ConvertFrom (from).GetIpv4 ());

    ProposedHeader receivedProposedHeader;
    packet->RemoveHeader(receivedProposedHeader);
    NS_LOG_INFO("" << receivedProposedHeader);
    
    int hopCount = (int) (receivedProposedHeader.GetHopCount());
    if(hopCount == 5) {
        std::cout << "[*] Hop-Count: " << (int)(receivedProposedHeader.GetHopCount()) << "\n";
        //std::cout << "delay " << (Simulator::Now().GetSeconds ()) - sentTime << "\n";
        const auto end = std::chrono::high_resolution_clock::now();
        const std::chrono::duration<double, std::milli> elapsed = end - sentTime;
        std::cout << "Waited " << elapsed.count() << '\n';
        if(repeatIdx >= repeatDataLength) {
            repeatIdx = 0;
            int sum = 0;
            for (int k=0; k<repeatDataLength; k++) {
                sum += delayData[testIdx][k];
            }
            delayData[testIdx][0] = sum / repeatDataLength;
            testIdx++;
        }
        delayData[testIdx][repeatIdx++] = elapsed.count();
    }


    size = packet->GetSize();

    packet->CopyData(packetParameters.packetData, size);
    NS_LOG_INFO ("" << "Packet data: " << packetParameters.packetData);



    for(i = 0; i < 12; ++i){
        packetParameters.packetData[i] += keys[receivedProposedHeader.GetHopCount()];
    }

    tempFlags = receivedProposedHeader.GetFlags();
    tempAddr = receivedProposedHeader.GetForwardAddresses();

    NS_LOG_INFO("" << "Decrypted Forward Address: " << Ipv4Address(tempAddr[0] + keys[receivedProposedHeader.GetHopCount()]));

    if(tempFlags[0] == 1)
    {
        for(i = 0; i < 4; ++i)
        {
            packetParameters.flags[i] = tempFlags[i + 1];
            packetParameters.addresses[i] = tempAddr[i + 1];
        }
        packetParameters.flags[4] = 0;
        packetParameters.addresses[4] = 0;
        packetParameters.hopCount = receivedProposedHeader.GetHopCount() + 1;
        SendStuff (socket, Ipv4Address (tempAddr[0] + keys[receivedProposedHeader.GetHopCount()]), port, packetParameters);
    }

}

void Create2DPlotFile()
{
  std::string fileNameWithNoExtension = "plot-2d";
  std::string graphicsFileName        = fileNameWithNoExtension + ".png";
  std::string plotFileName            = fileNameWithNoExtension + ".plt";
  std::string plotTitle               = "Message delay in the proposed structure";
  std::string dataTitle               = "Proposed structure";

  // Instantiate the plot and set its title.
  Gnuplot plot (graphicsFileName);
  plot.SetTitle (plotTitle);

  // Make the graphics file, which the plot file will create when it
  // is used with Gnuplot, be a PNG file.
  plot.SetTerminal ("png");

  // Set the labels for each axis.
  plot.SetLegend ("Maximum delay between two entities (ms)", "Message delay (ms)");

  // Set the range for the x axis.
  plot.AppendExtra ("set xrange [0:100]");

  // Instantiate the dataset, set its title, and make the points be
  // plotted along with connecting lines.
  Gnuplot2dDataset dataset;
  dataset.SetTitle (dataTitle);
  dataset.SetStyle (Gnuplot2dDataset::LINES_POINTS);

//   double x;
//   double y;

//   // Create the 2-D dataset.
//   for (x = -5.0; x <= +5.0; x += 1.0)
//     {
//       // Calculate the 2-D curve
//       // 
//       //            2
//       //     y  =  x   .
//       //  
//       y = x * x;

//       // Add this point.
//       dataset.Add (x, y);
//     }

for (int i=0;i<delayDataLength;i++) {
    dataset.Add(i, delayData[i][0]);
}

  // Add the dataset to the plot.
  plot.AddDataset (dataset);

  // Open the plot file.
  std::ofstream plotFile (plotFileName.c_str());

  // Write the plot file.
  plot.GenerateOutput (plotFile);

  // Close the plot file.
  plotFile.close ();
}
