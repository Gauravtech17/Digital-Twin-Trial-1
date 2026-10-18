export type Patient={id:string;code:string;display_name:string;age_band:string;created_at:string;synthetic:boolean};
export type Measurement={id:string;kind:string;value:number;unit:string;method:string;quality:string};
export type Observation={id:string;patient_id:string;assessment_id:string;observed_at:string;longest_mm:number;width_mm:number;depth_mm:number|null;volume_mm3:number|null;unit:string;method:string;provenance:string;quality:Record<string,unknown>;synthetic:boolean;measurements:Measurement[]};
export type Assessment={id:string;patient_id:string;status:string;started_at:string;completed_at:string|null;config:Record<string,unknown>;observation_id:string|null;error_message:string|null};
