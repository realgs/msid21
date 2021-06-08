export interface Resource {
    name: string;
    amount: number;
    meanPurchase: number;
}

export interface ResourceStats{
    name: string;
    currency: string;
    meanPurchase: number;
    recommendedSell: string;
    value: {full: ResourceValue; part: ResourceValue; partPercent: number};
    arbitration: ResourceArbitration[];
}

export interface ResourceValue{
    amount: number;
    price: number;
    profit: number;
    value: number;
}

export interface ResourceArbitration{
    api1: string;
    api2: string;
    currency1: string;
    currency2: string;
    profit: number;
    quantity: number;
    rate: number;
}