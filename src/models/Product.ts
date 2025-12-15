import mongoose, { Schema, Model, Document } from 'mongoose';

export interface IProduct extends Document {
    slug: string;
    name: string;
    description: string;
    basePrice: number;
    currency: 'USD' | 'UYU';
    specifications: {
        availableThicknesses: string[]; // e.g. ["50mm", "100mm"]
        hasColorOptions: boolean;
        availableColors?: string[];
    };
    metadata: {
        tags: string[];
        useCases: string[];
    };
}

const ProductSchema = new Schema<IProduct>({
    slug: { type: String, required: true, unique: true },
    name: { type: String, required: true },
    description: { type: String, required: true },
    basePrice: { type: Number, required: true }, // Base price for standard thickness (usually 100mm)
    currency: { type: String, enum: ['USD', 'UYU'], default: 'USD' },
    specifications: {
        availableThicknesses: { type: [String], required: true },
        hasColorOptions: { type: Boolean, default: false },
        availableColors: { type: [String], default: [] }
    },
    metadata: {
        tags: { type: [String], default: [] },
        useCases: { type: [String], default: [] }
    }
}, {
    timestamps: true
});

// Avoid OverwriteModelError
const Product = (mongoose.models.Product as Model<IProduct>) || mongoose.model<IProduct>('Product', ProductSchema);

export default Product;
